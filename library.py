#!/usr/bin/env python3
"""A library of research papers."""

import re
from csv import DictReader
from itertools import chain
from argparse import ArgumentParser
from collections import defaultdict
from inspect import signature, Parameter
from pathlib import Path
from subprocess import run
from textwrap import dedent
from typing import Any, Optional


BIBTEX_PATH = Path('~/Dropbox/pim/library.bib').expanduser().resolve()
PAPERS_PATH = Path('~/papers').expanduser().resolve()
REMOTE_HOST = 'justinnhli.com'
REMOTE_PATH = Path('/home/justinnhli/justinnhli.com/papers')

WEIRD_NAMES = {}


def load_weird_names():
    # type: () -> None
    """Read in weird names data."""
    with Path(__file__).parent.joinpath('entities.csv').open(encoding='utf-8') as fd:
        for row in DictReader(fd, delimiter='\t'):
            WEIRD_NAMES[row['author']] = row['short-name']


load_weird_names()

BIBTEX_FIELDS = [
    'id',
    'type',
    'address',
    'author',
    'booktitle',
    'doi',
    'editor',
    'edition',
    'howpublished',
    'institution',
    'journal',
    'month',
    'note',
    'number',
    'organization',
    'pages',
    'publisher',
    'school',
    'series',
    'title',
    'translator',
    'url',
    'venue',
    'volume',
    'year',
]

class Paper:
    """A research paper."""

    __slots__ = (
        # library fields
        'library',
        # bibtex fields
        *BIBTEX_FIELDS,
    )

    def __init__(self, paper_id, library=None):
        # type: (str, Optional[Library]) -> None
        """Initialize the Paper."""
        self.library = library
        self.id = paper_id # pylint: disable = invalid-name
        self.type = ''

    @property
    def directory(self):
        # type: () -> Path
        """Print the local library directory path."""
        if self.library:
            return self.library.directory
        else:
            return PAPERS_PATH

    @property
    def remote_host(self):
        # type: () -> str
        """Print the remote host."""
        if self.library:
            return self.library.remote_host
        else:
            return REMOTE_HOST

    @property
    def remote_path(self):
        # type: () -> Path
        """Print the remote library directory path."""
        if self.library:
            return self.library.remote_path
        else:
            return REMOTE_PATH

    @property
    def bibtex(self):
        # type: () -> str
        """Get a BibTex reference for the Paper."""
        lines = []
        lines.append(f'@{self.type} {{{self.id},')
        for attr in sorted(self.__slots__):
            if attr in ('id', 'type'):
                continue
            if hasattr(self, attr):
                lines.append(f'    {attr} = {{{getattr(self, attr)}}},')
        lines.append('}')
        return '\n'.join(lines)

    @property
    def path(self):
        # type: () -> Path
        """Get the path of the local file."""
        return self.local

    @property
    def local(self):
        # type: () -> Path
        """Get the path of the local file."""
        return self.directory / self.id.lower()[0] / (self.id + '.pdf')

    @property
    def remote(self):
        # type: () -> str
        """Get the URL of the remote file."""
        return 'https://' + str(Path(REMOTE_HOST, 'papers', self.id[0].lower(), self.id + '.pdf'))

    @property
    def pdfinfo(self):
        # type: () -> dict[str, str]
        """Read pdfinfo."""
        if not self.local.exists():
            raise FileNotFoundError(self.local)
        pdfinfo = {}
        for line in _run_shell_command('pdfinfo', str(self.local)).splitlines():
            key, value = line.split(':', maxsplit=1)
            value = value.strip()
            pdfinfo[key] = value
        return pdfinfo


class Library:
    """A Library of research Papers."""

    def __init__(
        self,
        directory=PAPERS_PATH,
        bibtex_path=BIBTEX_PATH,
        remote_host=REMOTE_HOST,
        remote_path=REMOTE_PATH,
    ):
        # type: (Path, Path, str, Path) -> None
        """Initialize the Library."""
        self.directory = directory
        self.bibtex_path = bibtex_path
        self.remote_host = remote_host
        self.remote_path = remote_path
        self.papers = {} # type: dict[str, Paper]
        self._read_bibtex()

    def __contains__(self, key):
        # type: (Any) -> bool
        return key in self.papers

    def __getitem__(self, key):
        # type: (Any) -> Paper
        return self.papers[key]

    def _read_bibtex(self):
        # type: () -> None
        with self.bibtex_path.open(encoding='utf-8') as fd:
            paper = None
            for line in fd:
                line = line.rstrip()
                if not line or re.fullmatch(r'\s*%.*', line):
                    continue
                if line.startswith('@'):
                    match = re.fullmatch('@(?P<type>[^ ]+) *{(?P<id>[^,]+),', line)
                    assert match, f'anomalous bibtex entry: {line}'
                    paper = Paper(match.group('id'), library=self)
                    paper.type = match.group('type')
                elif line.startswith('}'):
                    self.papers[paper.id] = paper
                    paper = None
                else:
                    match = re.fullmatch(r'\s*(?P<attr>[^ =]+) *= *{(?P<val>.+)},', line)
                    assert match, f'anomalous bibtex field: {line}'
                    assert not hasattr(paper, match.group('attr')), f'{paper.id} has duplicate values for {match.group("attr")}'
                    setattr(paper, match.group('attr'), match.group('val').strip())

    # individual paper management

    def add(self, file_path, new_name=None):
        # type: (Path, Optional[str]) -> None
        """Add paper to library.

        Parameters:
            file_path (str): The file path to add.
            new_name (str): The new name for the file. Optional.
        """
        old_path = Path(file_path).expanduser().resolve()
        if new_name is None:
            new_name = old_path.stem
        elif new_name.endswith('.pdf'):
            new_name = new_name[:-4]
        new_path = Path(self.directory, new_name[0].lower(), new_name + '.pdf')
        assert not new_path.exists(), f'file already exists: {new_path}'
        old_path.replace(new_path)

    def open(self, *file_path_strs):
        # type: (*str) -> None
        """Open the paper in a PDF reader.

        Parameters:
            *file_path_strs (str): The file path to open
        """
        for file_path_str in file_path_strs:
            _run_shell_command('open', str(Path(file_path_str).expanduser().resolve()))

    def remove(self, *file_path_strs):
        # type: (*str) -> None
        """Remove the paper from the library.

        Parameters:
            *file_path_strs (Path): The file paths to remove.
        """
        for file_path_str in file_path_strs:
            if not file_path_str.endswith('.pdf'):
                file_path_str += '.pdf'
            file_path = Path(self.directory, file_path_str[0].lower(), file_path_str)
            file_path.expanduser().resolve().unlink(missing_ok=True)

    # individual paper pass through

    def passthrough(self, name, operation='default'):
        # type: (str, str) -> None
        """Pass through operation to paper."""
        print(name, operation)
        raise NotImplementedError()

    # library management

    def path(self, *names):
        # type: (*str) -> None
        """Print local filepaths of papers."""
        for name in names:
            if name.endswith('.pdf'):
                name = name[:-4]
            print(self.papers[name].path)

    def lint(self): # pylint: disable = too-many-statements
        # type: () -> None
        """Lint the library bibtex file."""

        def check_names(key, paper):
            # type: (str, Paper) -> None
            """Check for non "last, first" authors and editors."""

            def check_name(attr):
                # type: (str) -> None
                if not hasattr(paper, attr):
                    return
                value = getattr(paper, attr)
                if value in WEIRD_NAMES:
                    return
                people = value.split(' and ')
                if any((',' not in person) for person in people if person not in WEIRD_NAMES):
                    pattern = ' *(?P<first>[A-Z][^ ]*( +[A-Z][^ ]*)*) +(?P<last>.*) *'
                    suggestion = ' and '.join([
                        person.strip() if person in WEIRD_NAMES
                        else re.sub(
                            pattern,
                            (lambda match: match.group('last') + ', ' + match.group('first')),
                            person)
                        for person in people
                    ])
                    print(dedent(f'''
                        non-conforming {attr}s in {key}:
                            current:
                                {attr} = {{{value}}},
                            suggested:
                                {attr} = {{{suggestion}}},
                    ''').strip())

            for attr in ['editor', 'author']:
                check_name(attr)

        def check_id(key, paper):
            # type: (str, Paper) -> None
            """Check for incorrectly-formed IDs."""
            if hasattr(paper, 'author'):
                author = getattr(paper, 'author')
            else:
                author = getattr(paper, 'editor')
            if author.startswith('{'):
                first_author = re.sub('({[^}]*}).*', r'\1', author)
                first_author = WEIRD_NAMES.get(first_author, first_author)
            else:
                first_author = author.split(',')[0]
                first_author = re.sub(r'\\.{(.)}', r'\1', first_author)
            title = getattr(paper, 'title').title()
            year = getattr(paper, 'year')
            if year == 'FIXME':
                return
            suggestion = f'{first_author}{year}{title}'
            suggestion = re.sub('[^0-9A-Za-z]', '', suggestion)
            short_suggestion = f'{first_author}{year}{"".join(title.split()[:3])}'
            short_suggestion = re.sub('[^0-9A-Za-z]', '', short_suggestion)
            suffices = ('', '1', '2', 'thesis')
            matches = False
            for suffix in suffices:
                if suffix and key.lower().endswith(suffix):
                    temp_key = key[:-len(suffix)]
                else:
                    temp_key = key
                if suggestion.lower().startswith(temp_key.lower()):
                    matches = True
                    break
            if not matches:
                print(dedent(f'''
                    non-conforming ID for {key}:
                        current:
                            @{paper.type} {{{key},
                        suggestions:
                            @{paper.type} {{{short_suggestion},
                            @{paper.type} {{{suggestion},
                ''').strip())

        def check_spaces(key, paper):
            # type: (str, Paper) -> None
            """Strip leading/trailing spaces and remove multiple spaces."""
            for attr in BIBTEX_FIELDS:
                if not hasattr(paper, attr):
                    continue
                value = getattr(paper, attr)
                new_value = re.sub('  +', ' ', value.strip())
                if value != new_value:
                    print(dedent(f'''
                        leading/trailing/multiple spaces in {attr} of {key}:
                            suggestion:
                                {attr} = {{{new_value}}},
                    ''').strip())

        def check_capitalization(key, paper):
            # type: (str, Paper) -> None
            """Check for unquoted capitalizations."""
            unquoted_regexes = [
                r'(?P<word>[^ ]*[A-Za-z][A-Z][^ ]*)',
                r'\? (?P<word>\w+)',
            ]
            for attr in ['title', 'booktitle', 'journal']:
                if not hasattr(paper, attr):
                    continue
                title = getattr(paper, attr)
                unnested_title = title
                while '{' in unnested_title:
                    unnested_title = re.sub('{[^{}]*}', '', unnested_title)
                matches = list(chain(*(re.finditer(regex, unnested_title) for regex in unquoted_regexes)))
                if not matches:
                    continue
                words = set(
                    re.sub(r'^\W*(.*?)\W*$', r'\1', match.group('word'))
                    for match in matches
                )
                new_title = title
                for word in words:
                    new_title = re.sub(r'\b' + re.escape(word) + r'\b', '{' + word + '}', new_title)
                    new_title = new_title.replace('{{' + word + '}}', '{' + word + '}')
                if new_title != title:
                    print(dedent(f'''
                        unquoted {attr} for {key}:
                            current:
                                {attr} = {{{title}}},
                            suggestion:
                                {attr} = {{{new_title}}},
                    ''').strip())

        def check_ordinals(key, paper):
            # type: (str, Paper) -> None
            """Check for non-superscript ordinals."""
            for attr in ('booktitle', 'title', 'journal'):
                if not hasattr(paper, attr):
                    continue
                val = getattr(paper, attr)
                match = re.search('(.*[^0-9][0-9]+)(st|nd|rd|th)(.*)', val)
                if match:
                    suggestion = f'{match.group(1)}\\textsuperscript{{{match.group(2)}}}{match.group(3)}'
                    print(dedent(f'''
                        non-superscript ordinal in {attr} of {key}:
                            suggestion:
                                {attr} = {{{suggestion}}},
                    ''').strip())

        def check_doi(key, paper):
            # type: (str, Paper) -> None
            """Check for DOIs not in URL format."""
            if not hasattr(paper, 'doi'):
                return
            doi = getattr(paper, 'doi')
            if not doi.startswith('https://doi.org/'):
                suggestion = re.sub('.*?(10.*)', r'\1', doi)
                print(dedent(f'''
                    DOI in non-URL format for {key}:
                        suggestion:
                            doi = {{https://doi.org/{suggestion}}},
                ''').strip())

        def check_pages(key, paper):
            # type: (str, Paper) -> None
            """Check for improper pages."""
            if not hasattr(paper, 'pages'):
                return
            pages = getattr(paper, 'pages')
            if pages.isdigit() or pages == 'FIXME':
                return
            if ' ' in pages or '--' not in pages:
                if '-' in pages:
                    start, end = pages.split('-')
                    start = start.strip()
                    end = end.strip()
                    print(dedent(f'''
                        pages not in <start>--<end> format for {key}
                            suggestion:
                                pages = {{{start}--{end}}},
                    ''').strip())
                else:
                    print(dedent(f'''
                        pages not in <start>--<end> format for {key}
                            current:
                                pages = {{{pages}}},
                    ''').strip())

        def check_latex(key, paper):
            # type: (str, Paper) -> None
            """Check for LaTeX special characters."""
            for attr in ('booktitle', 'title', 'journal'):
                if not hasattr(paper, attr):
                    continue
                val = getattr(paper, attr)
                index = val.find('&')
                if index == -1:
                    continue
                if val[index - 1] != '\\':
                    suggestion = re.sub(r'([^\\])&', r'\1\&', val)
                    print(dedent(f'''
                        {attr} field contains unescaped & for {key}
                            suggestion:
                                {suggestion}
                    ''').strip())

        def check_files():
            # type: () -> None
            """Check for papers not in the index."""
            filenames = {
                pdf_path.stem: pdf_path
                for pdf_path in PAPERS_PATH.glob('**/*.pdf')
            }
            unindexed_files = set(filenames) - set(self.papers)
            for pdf in unindexed_files:
                print(f'no entry for file: {filenames[pdf]}')

        for key, paper in self.papers.items():
            check_names(key, paper)
            check_id(key, paper)
            check_spaces(key, paper)
            check_capitalization(key, paper)
            check_ordinals(key, paper)
            check_doi(key, paper)
            check_pages(key, paper)
            check_latex(key, paper)
        check_files()

    def toc(self, out_path=None):
        # type: (Optional[Path]) -> None
        """Create an index HTML file of the library."""
        lines = ['''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
                    <title>Paper Archive Contents</title>
                </head>
                <body>
        ''']
        for paper_id, paper in sorted(self.papers.items()):
            paper_type = paper.type
            url = _get_url(paper_id)
            lines.append(f'<pre id="{paper_id}">')
            lines.append(f'@{paper_type} {{<a href="{url}">{paper_id}</a>,')
            for attr in paper.__slots__:
                if attr in ('library', 'id', 'type') or not hasattr(paper, attr):
                    continue
                value = getattr(paper, attr)
                lines.append(f'    {attr} = {{{value}}},')
            lines.append('}')
            lines.append('</pre>')
            lines.append('')
        lines.append('''
                </body>
            </html>
        ''')
        output = '\n'.join(lines)
        if out_path is None:
            print(output)
        else:
            with out_path.open('w') as fd:
                fd.write(output)
                fd.write('\n')

    def unify(self):
        # type: () -> None
        """Find and unify names."""
        coauthors = defaultdict(list) # type: dict[str, list[tuple[str, str]]]
        for key, paper in self.papers.items():
            authors = getattr(paper, 'author').split(' and ')
            for author1 in authors:
                for author2 in authors:
                    author2 = re.sub('[^A-Za-z, ]', '', author2)
                    coauthors[author1].append((author2, key))
        for author, coauthor_info in sorted(coauthors.items()):
            coauthor_info = sorted(coauthor_info)
            printed = False
            for (author1, _), (author2, _) in zip(coauthor_info[:-1], coauthor_info[1:]):
                if author1 != author2 and author2.startswith(author1.strip('.')):
                    if not printed:
                        print(author)
                        printed = True
                    print('   ', author1)
                    print('   ', author2)

    def search(self, *terms):
        # type: (*str) -> None
        """Search for a paper."""
        raise NotImplementedError()

    # remote management

    def url(self, *names):
        # type: (str) -> None
        """Print URLs of papers."""
        for name in names:
            if name.endswith('.pdf'):
                name = name[:-4]
            print(_get_url(name))

    def diff(self):
        # type: () -> None
        """List papers that differ between the local and remote libraries."""
        output = _run_shell_command(
            'rsync',
            '--archive',
            '--verbose',
            '--dry-run',
            '--delete',
            f'{self.remote_host}:{self.remote_path}/',
            str(self.directory),
        )
        remote = set()
        local = set()
        for line in output.splitlines()[1:-3]:
            line = line.strip()
            if not line or line.endswith('/'):
                continue
            if line.startswith('deleting'):
                local.add(line[9:])
            else:
                remote.add(line)
        for line in sorted(remote.union(local)):
            if line in local and line in remote:
                print(f'! {line}')
            elif line in local:
                print(f'< {line}')
            else:
                print(f'> {line}')

    def pull(self):
        # type: () -> None
        """Download remote papers to the local library."""
        print(_run_shell_command(
            'rsync',
            '--archive',
            '--progress',
            '--rsh=ssh',
            '--exclude', '.*',
            f'{self.remote_host}:{self.remote_path}/',
            str(self.directory),
        ))

    def push(self):
        # type: () -> None
        """Upload local papers to the remote library."""
        print(_run_shell_command(
            'rsync',
            '--archive',
            '--progress',
            '--rsh=ssh',
            '--exclude', '.*',
            f'{self.directory}/',
            f'{self.remote_host}:{self.remote_path}',
        ))

    def sync(self):
        # type: () -> None
        """Sync the remote and local libraries.

        Equivalent to a pull, then a push.
        """
        self.pull()
        self.toc(out_path=self.directory.joinpath('index.html'))
        self.push()

    # as command line

    def __call__(self):
        # type: () -> None
        # create the top-level parser
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        var_positionals = {}
        for obj in [self, Paper]:
            for attr in dir(obj):
                func = getattr(obj, attr)
                if attr.startswith('_'):
                    continue
                if isinstance(func, property):
                    continue
                if not hasattr(func, '__call__'):
                    continue
                if func.__doc__ is not None:
                    description = func.__doc__.splitlines()[0]
                else:
                    description = None
                subparser = subparsers.add_parser(attr, help=description)
                for name, parameter in signature(func).parameters.items():
                    arg_name = name
                    if parameter.kind == Parameter.VAR_POSITIONAL:
                        var_positionals[attr] = name
                        subparser.add_argument(arg_name, nargs='*')
                    elif parameter.default != Parameter.empty:
                        subparser.add_argument(arg_name, default=parameter.default, nargs='?')
                    else:
                        subparser.add_argument(arg_name)
                subparser.set_defaults(_name=attr, func=func)
        args = vars(parser.parse_args())
        if '_name' not in args:
            parser.error('no action specified')
        var_arg = var_positionals.get(args['_name'], '')
        args['func'](
            *args.get(var_arg, []),
            **{
                k.replace('-', '_'): v for k, v in args.items()
                if k not in ('_name', 'func', var_arg)
            },
        )


def _get_url(filepath_str):
    # type: (str) -> str
    filepath = Path(filepath_str)
    return 'https://' + str(Path(REMOTE_HOST, 'papers', filepath.name[0].lower(), filepath.stem + '.pdf'))


def _run_shell_command(command, *args):
    # type: (str, *str) -> str
    print(command + ' ' + ' '.join(
        (arg if arg.startswith('-') else f'"{arg}"')
        for arg in args
    ))
    return run([command, *args], capture_output=True, check=True).stdout.decode('utf-8')


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    Library()()


if __name__ == '__main__':
    main()
