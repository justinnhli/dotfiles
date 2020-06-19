#!/usr/bin/env python3
"""Sheaf: A note-taking tool."""

import re
from argparse import ArgumentParser
from collections import namedtuple
from datetime import date as Date
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit

from util import DATE_REGEX, run_with_venv, titlize, filenamize
from library import Library
from archive import Archive

try:
    from newspaper import Article as NewspaperArticle
except ModuleNotFoundError as err:
    run_with_venv('sheaf')

# paths

SUFFIX = '.shf'
SHEAF_PATH = Path('~/pim/sheaf').expanduser().resolve()

# classes


class Reference:
    """A Sheaf reference."""

    REGEX = re.compile(r'\[\[[^]]*\]\]')

    def __init__(self, text):
        self.text = text.strip('[]').strip()
        self.canonical = re.sub('[^-0-9a-z ]', '', self.text.lower())

    def __bool__(self):
        return bool(self.text)

    def __eq__(self, other):
        return self.canonical == other.canonical

    @property
    def title(self):
        return titlize(self.text)

    @property
    def filename(self):
        return filenamize(self.text)

    @property
    def reference(self):
        return f'[[{self.text}]]'

    @staticmethod
    def create_all(string):
        for text in Reference.REGEX.findall(string):
            yield Reference(text)


Metadatum = namedtuple('Metadatum', 'read, write')


class Page:
    """A Sheaf page."""

    METADATA = {
        'short_title': Metadatum(
            read=(lambda string: Reference(string)),
            write=(lambda metadatum: metadatum.reference if metadatum else ''),
        ),
        'synonyms': Metadatum(
            read=(lambda string: list(Reference.create_all(string))),
            write=(lambda metadatum: ' '.join(synonym.reference for synonym in metadatum)),
        ),
        'tags': Metadatum(
            read=(lambda string: list(re.findall('#[0-9A-Za-z:]*', string))),
            write=(lambda metadatum: ' '.join(tag for tag in metadatum)),
        ),
        'url': Metadatum(
            read=(lambda string: string),
            write=(lambda metadatum: metadatum),
        ),
        'creators': Metadatum(
            read=(lambda string: list(creator.strip() for creator in string.split(','))),
            write=(lambda metadatum: ' '.join(creator for creator in metadatum)),
        ),
        'archived': Metadatum(
            read=(lambda string: Reference(string)),
            write=(lambda metadatum: metadatum.reference if metadatum else ''),
        ),
    }

    def __init__(self, filepath):
        # type: (Path) -> None
        """Initialize the Page.

        Parameters:
            filepath (Path): The path of the Sheaf file.
        """
        self.filepath = filepath
        self.raw_contents = ''
        self.title = None # type: Optional[Reference]
        self.metadata = {} # type: Dict[str, str]
        self.contents = ''
        self._read_page()

    @property
    def short_title(self):
        return self.metadata.get('short_title', None)

    @property
    def synonyms(self):
        return self.metadata.get('synonyms', [])

    @property
    def tags(self):
        return self.metadata.get('tags', [])

    @property
    def url(self):
        return self.metadata.get('url', '')

    @property
    def creators(self):
        return self.metadata.get('creators', [])

    @property
    def archived(self):
        return self.metadata.get('archived', None)

    @property
    def slug(self):
        if self.short_title:
            return self.short_title.filename
        else:
            return self.title.filename

    @property
    def references(self):
        # type: () -> Generator[str, None, None]
        """Get the references in the Page.

        Yields:
            str: The references.
        """
        yield from Reference.create_all(self.contents)

    @property
    def is_empty(self):
        return '#unread' not in self.tags and self.contents.strip() == ''

    @property
    def is_media(self):
        return any([self.url, self.creators, self.archived])

    def _read_page(self):
        # type: () -> None
        """Read the page file."""
        with self.filepath.open() as fd:
            self.raw_contents = fd.read().replace('\n\n\n', '\n\n')
        lines = self.raw_contents.splitlines()
        self.title = Reference(lines[0])
        in_metadata = False
        line_index = 0
        for line_index, line in enumerate(lines):
            if line == 'metadata':
                in_metadata = True
            elif in_metadata:
                if not line.startswith(' '):
                    in_metadata = False
                    break
                key, value = line.split(':', maxsplit=1)
                key = key.strip().replace(' ', '_')
                value = value.strip()
                if key not in self.METADATA:
                    print(f'WARNING: Unrecognized metadata {key} in {self.filepath}; skipping...')
                    continue
                self.metadata[key] = self.METADATA[key].read(value)
        if in_metadata and line_index == len(lines) - 1:
            self.contents = ''
        else:
            self.contents = '\n'.join(lines[line_index - 1:])

    def write(self, filepath=None):
        # type: (Optional[Path]) -> None
        """Read the page file."""
        if filepath is None:
            filepath = self.filepath
        with filepath.open('w') as fd:
            fd.write(self.regenerate())
            fd.write('\n')

    def rename(self, slug):
        # type: (str) -> None
        """Rename the Page."""
        new_filepath = get_path(slug)
        assert not new_filepath.exists(), f'{new_filepath} already exists'
        self.write(new_filepath)
        self.filepath.unlink()
        self.filepath = new_filepath

    def regenerate(self):
        lines = []
        lines.append(self.title.text)
        lines.append('')
        lines.append('metadata')
        if self.short_title:
            lines.append(f'    short title: {self.METADATA["short_title"].write(self.short_title)}')
        if not self.is_media:
            lines.append(f'    synonyms: {self.METADATA["synonyms"].write(self.synonyms)}')
        lines.append(f'    tags: {self.METADATA["tags"].write(self.tags)}')
        for attribute in ['url', 'creators', 'archived']:
            value = getattr(self, attribute)
            if value:
                lines.append(f'    {attribute}: {self.METADATA[attribute].write(value)}')
        lines.extend(self.contents.splitlines())
        return '\n'.join(line.rstrip() for line in lines)

    def delete(self):
        # type: () -> None
        """Delete the Page."""
        self.filepath.unlink()

    @staticmethod
    def create(filename, title, tags=None, metadata=None, contents=''):
        # type: (str, str, Optional[Set[str]], Optional[Mapping[str, str]], str) -> Page
        # pylint: disable = f-string-without-interpolation
        """Create a new Page.

        Parameters:
            filename (str): The filename for the Page.
            title (str): The title of the Page.
            tags (Set[str]): The tags for the Page.
            metadata (Mapping[str, str]): Additional metadata for the Page.
            contents (str): The contents of the Page.

        Returns:
            Page: The resulting Page.
        """
        if tags is None:
            tags = set()
        if metadata is None:
            metadata = {}
        lines = [
            f'{title}',
            f'',
            f'metadata',
            f'    short title:',
            f'    synonyms:',
            f'    tags: {" ".join(sorted(tags))}',
        ]
        for key, value in metadata.items():
            lines.append(f'    {key}: {value}')
        if contents:
            lines.extend(contents.splitlines())
        filepath = get_path(filename)
        with filepath.open('w') as fd:
            fd.write('\n'.join(line.rstrip() for line in lines))
        return Page(filepath)


class Sheaf:
    """A Sheaf of Pages."""

    def __init__(self, directory):
        # type: (Path) -> None
        """Initialize the Sheaf.

        Parameters:
            directory (Path): The directory path of the Sheaf Pages.
        """
        self.directory = directory
        self.archive = Archive()
        self.library = Library()
        self.pages = {} # type: Dict[Path, Page]
        self.tags = {} # type: Dict[str, Page]
        self._read_pages()
        self._collect_tags()

    def _read_pages(self):
        # type: () -> None
        """Read the pages in the Sheaf."""
        for page_path in self.directory.glob('**/*' + SUFFIX):
            page = Page(page_path)
            assert page.filepath not in self.pages, f'duplicate slug: {page.slug}'
            self.pages[page.filepath] = page

    def _collect_tags(self):
        # type: () -> None
        """Collect tags from the Pages."""
        self.tags = {}
        for page in self.pages.values():
            tags = set(synonym.text for synonym in page.synonyms)
            tags.add(page.title.text)
            if page.short_title:
                tags.add(page.short_title.text)
            if page.url:
                tags.add(page.url)
            for tag in tags:
                self.tags[tag] = page

    def create(self, title, filename=None, tags=None, contents=''):
        if title.lower() in self.tags:
            return self.tags[title.lower()]
        else:
            if filename is None:
                filename = filenamize(title)
            if filename in self.pages:
                return self.pages[filename]
            page = Page.create(
                filename=filename,
                title=title,
                tags=tags,
                contents=contents,
            )
            self.pages[page.filepath] = page
            return page

    # download functions

    def download(self, *urls):
        # type: (*str) -> Page
        """Archive a URL and create a Page for it.

        Parameters:
            *urls (str): The URL of the article.

        Returns:
            Page: The resulting Page.
        """
        pages = []
        for url in urls:
            article = self.archive.add(url)
            assert article.title.strip(), 'blank article title'
            if url in self.tags:
                pages.append(self.tags[url])
            else:
                pages.append(self.create(
                    filename=filenamize(article.title),
                    title=article.title,
                    tags=set(['#unread',]),
                    contents='\n'.join([
                        f'    url: {article.url}',
                        f'    creators: {", ".join(article.authors)}',
                        f'    archived: [[{article.accessed}]]',
                    ]),
                ))
        return pages

    # graph functions

    def graph(self):
        raise NotImplementedError()

    # index functions

    def _delete_pages(self):
        # type: () -> None
        """Delete pages tagged with #delete."""
        to_delete = set(
            slug for slug, page in self.pages.items()
            if '#delete' in page.tags or page.is_empty
        )
        for slug in to_delete:
            self.pages[slug].delete()
            del self.pages[slug]

    def _rename_pages(self):
        # type: () -> None
        """Rename Pages whose slugs don't match their filename."""
        for page in self.pages.values():
            if page.filepath.name != page.slug + SUFFIX:
                page.rename(page.slug + SUFFIX)

    def _write_tags_file(self):
        # type: () -> None
        """Write the tags file."""
        lines = []
        for tag, page in sorted(self.tags.items()):
            lines.append('\t'.join([tag, str(page.filepath.relative_to(self.directory)), '1']))
        with self.directory.joinpath('.tags').open('w') as fd:
            for line in sorted(lines, key=(lambda line: line.lower())):
                fd.write(line + '\n')

    def _list_dangling_references(self):
        # type: () -> None
        """Print references to nonexistent pages."""
        for slug, page in self.pages.items():
            missing = []
            for ref in page.references:
                if DATE_REGEX.fullmatch(ref.text):
                    continue
                if ref.text in self.library:
                    continue
                if ref.text.startswith('journal::') and DATE_REGEX.fullmatch(ref.text[-10:]):
                    continue
                if ref.text.lower() not in self.tags:
                    missing.append(ref)
            if missing:
                print(slug)
                for ref in missing:
                    print(f'    {ref.text.lower()}')

    def _sync_archive(self):
        # type: () -> None
        for page in self.pages.values():
            if not page.url:
                continue
            if 'youtube.com' in page.url:
                continue
            if '#NoIndex' in page.tags:
                continue
            if page.url not in self.archive:
                print(f'downloading {page.url}')
                self.archive.add(page.url)

    def _write_cache(self):
        pass # TODO

    def index(self, *_):
        # type: (*Any) -> None
        """Update index and metadata files."""
        # TODO update backlinks?
        self._delete_pages()
        self._rename_pages()
        self._write_tags_file()
        self._write_cache()
        self._sync_archive()
        self._list_dangling_references()

    # suggest functions

    def suggest(self, filepath):
        root_page = Page(Path(filepath))
        print('Backlinks')
        for page in self.pages.values():
            if page.filepath == root_page.filepath:
                continue
            if root_page.title not in page.references:
                continue
            print(page.title.reference)
            stack = []
            for line in page.raw_contents.splitlines():
                indent = (len(line) - len(line.lstrip())) // 4
                stack = stack[:indent]
                stack.append(line)
                # FIXME better check for if reference is in line
                if root_page.title.text.lower() in line.lower():
                    for line in stack:
                        print(line)
        print('Search Results')
        print('Clusters')

    # vimgrep functions

    def vimgrep(self, *terms):
        # type: (*str) -> None
        """List search results in vim :grep format."""
        # initialize a results dictionary
        results = {
            'url': [],
            'title': [],
            'new': [],
            'metadata': [],
            'text': [],
        }
        # find all matches pages first
        matches = []
        for page in self.pages.values():
            if all(term.lower() in page.raw_contents.lower() for term in terms):
                matches.append(page)
        # deal with special cases that could create new pages
        if len(terms) == 1 and terms[0].startswith('http'):
            # if it's a URL, download the article
            results['url'].append(self.download(terms[0])[0])
        elif len(terms) > 1 or not terms[0].startswith('#'):
            # if it's not a tag, create a new page with the exact search terms
            results['new'].append(self.create(titlize(*terms)))
        # loop through matches and group by type (not mutually exclusive)
        for page in matches:
            # check title
            if any(term.lower() in page.title.text.lower() for term in terms):
                results['title'].append(page)
            # check metadata
            for key in Page.METADATA:
                value = Page.METADATA[key].write(getattr(page, key))
                if any((term.lower() in value.lower()) for term in terms):
                    results['metadata'].append(page)
                    break
            # otherwise, generic content match
            results['text'].append(page)
        # output
        for category, cat_dict in results.items():
            if not cat_dict:
                continue
            print(category.upper())
            for page in sorted(cat_dict, key=(lambda page: getattr(page, 'title').text)):
                if page.contents == '':
                    snippet = page.raw_contents.replace('\n', ' ')
                else:
                    snippet = page.contents.replace('\n', ' ')
                print(f'{page.filepath}:1:{snippet}')
            print()



def get_path(filename):
    # type: (str) -> Path
    """Convert a Page filename to a Path."""
    if not filename.endswith(SUFFIX):
        return SHEAF_PATH / (filename + SUFFIX)
    else:
        return SHEAF_PATH / filename


# operations


def do_intake(sheaf, args):
    # type: () -> Generator[str, None, None]
    """Archive new links from Dynalist."""
    # TODO flesh out intake system
    with (Path(__file__).parent / 'dynalist.mock').open() as fd:
        lines = fd.read().splitlines()
    inbox_index = lines.index('inbox')
    link_regex = re.compile(r'\[(?P<title>.*)\]\((?P<url>.*)\)')
    for link in lines[inbox_index + 1:]:
        link = link.strip()
        if link.startswith('http'):
            url = link
        else:
            match = link_regex.fullmatch(link.strip())
            if match:
                url = match.group('url')
            else:
                print(f'failed to parse {link}')
                continue
        sheaf.download(url)


def do_rewrite(sheaf, args):
    # type: () -> None
    for page in sheaf.pages.values():
        with page.filepath.open() as fd:
            old_contents = fd.read()
        new_contents = page.regenerate()
        if old_contents.strip() != new_contents.strip():
            old_lines = old_contents.splitlines()
            new_lines = new_contents.splitlines()
            print(f'Page {page.title} does not match')
            if len(old_lines) != len(new_lines):
                print(f'different lengths: {len(old_lines)} vs. {len(new_lines)}')
            for line_num, (old, new) in enumerate(zip(old_lines, new_lines), start=1):
                if old != new:
                    print(f'{page.filepath}:{line_num}:different')
                    print('    old: ' + old)
                    print('    new: ' + new)


# main


def build_arg_parser(parser):
    actions = ['graph', 'index', 'intake', 'suggest', 'vimgrep', 'rewrite']
    parser.usage = 'test' # FIXME
    parser.add_argument('action', choices=actions, nargs='?', default='vimgrep')
    parser.add_argument('--sheaf-directory', default=SHEAF_PATH, type=Path)
    parser.add_argument('args', nargs='*')
    parser.set_defaults(function=parse_args)
    return parser


def parse_args(arg_parser, args):
    # type: (*str) -> None
    """Parse CLI arguments."""
    sheaf = Sheaf(SHEAF_PATH)
    do_functions = globals()
    if f'do_{args.action}' in do_functions:
        do_functions[f'do_{args.action}'](sheaf, args)
    elif hasattr(sheaf, args.action):
        getattr(sheaf, args.action)(*args.args)
    else:
        raise NotImplementedError(args.action)


def main():
    # type: () -> None
    arg_parser = build_arg_parser(ArgumentParser())
    args = arg_parser.parse_args()
    args.function(arg_parser, args)


if __name__ == '__main__':
    main()
