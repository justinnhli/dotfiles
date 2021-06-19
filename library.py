#!/usr/bin/env python3
"""A library of research papers."""

import re
from argparse import ArgumentParser
from collections import defaultdict
from distutils.spawn import find_executable
from inspect import signature, Parameter
from pathlib import Path
from subprocess import run
from typing import Any, Dict


BIBTEX_PATH = Path('~/pim/library.bib').expanduser().resolve()
PAPERS_PATH = Path('~/papers').expanduser().resolve()
REMOTE_HOST = 'justinnhli.com'
REMOTE_PATH = Path('/home/justinnhli/justinnhli.com/papers')


WEIRD_NAMES = {
    'Computing Research Association': 'CRA',
    'Liberal Arts Computer Science Consortium': 'LACS',
    'The College Board': 'CB',
    'The Join Task Force on Computing Curricula': 'JTFCC',
    'Open Science Collaboration': 'OSC',
    'others': '',
    '{Google Inc.}': 'Google',
    '{Gallup Inc.}': 'Gallup',
    '{National Academies of Sciences, Engineering, and Medicine}': 'NASEM',
    '{UMBEL Project}': 'UMBEL',
    '{The ABC Research Group}': 'ABC',
    '{The Economist}': 'Economist',
}

class Paper:
    """A research paper."""

    __slots__ = [
        # library fields
        'library',
        # bibtex fields
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

    def __init__(self, paper_id, library=None):
        # type: (str) -> None
        """Initialize the Paper."""
        self.library = library
        self.id = paper_id # pylint: disable = invalid-name
        self.type = ''

    @property
    def directory(self):
        if self.library:
            return self.library.directory
        else:
            return PAPERS_PATH

    @property
    def remote_host(self):
        if self.library:
            return self.library.remote_host
        else:
            return REMOTE_HOST

    @property
    def remote_path(self):
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
        if not self.local.exists():
            raise FileNotFoundError(self.local)
        process = run(['pdfinfo', str(self.local)], capture_output=True, check=True)
        stdout = process.stdout.decode('utf-8')
        print(stdout)
        # TODO parse pdfinfo


class Library:
    """A Library of research Papers."""

    def __init__(self, directory=PAPERS_PATH, bibtex_path=BIBTEX_PATH, remote_host=REMOTE_HOST, remote_path=REMOTE_PATH):
        # type: (Path, Path) -> None
        """Initialize the Library."""
        self.directory = directory
        self.bibtex_path = bibtex_path
        self.remote_host = remote_host
        self.remote_path = remote_path
        self.papers = {} # type: Dict[str, Paper]
        self._read_bibtex()

    def __contains__(self, key):
        # type: (Any) -> bool
        return key in self.papers

    def __getitem__(self, key):
        # type: (Any) -> Paper
        return self.papers[key]

    def _read_bibtex(self):
        # type: () -> None
        with self.bibtex_path.open() as fd:
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
                    match = re.fullmatch(' *(?P<attr>[^ =]+) *= *{(?P<val>.+)},', line)
                    assert match, f'anomalous bibtex field: {line}'
                    setattr(paper, match.group('attr'), match.group('val'))

    # individual paper management

    def add(self, file_path, new_name=None):
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

    def open(self, file_path):
        """Open the paper in a PDF reader.

        Parameters:
            file_path (str): The file path to open
        """
        # pylint: disable = no-self-use
        run(['open', str(Path(file_path).expanduser().resolve())], check=True)

    def remove(self, *file_paths):
        """Remove the paper from the library.

        Parameters:
            file_paths (Iterable[str]): The file paths to remove.
        """
        for file_path in file_paths:
            if file_path.endswith('.pdf'):
                file_path = file_path[:-4]
            Path(self.directory, file_path[0].lower(), file_path + '.pdf').expanduser().resolve().unlink()

    # individual paper pass through

    def passthrough(self, name, operation='default'):
        # pylint: disable = no-self-use
        print(name, operation)
        raise NotImplementedError()

    # library management

    def lint(self):
        """Lint the library bibtex file."""
        for key, paper in sorted(self.papers.items()):
            # check for non "last, first" authors and editors
            for attr in ['editor', 'author']:
                if not hasattr(paper, attr):
                    continue
                value = getattr(paper, attr)
                if value in WEIRD_NAMES:
                    continue
                people = value.split(' and ')
                if any((',' not in person) for person in people if person not in WEIRD_NAMES):
                    print(f'non-conforming {attr}s in {key}:')
                    print(f'    current:')
                    print(f'        {attr} = {{{value}}},')
                    pattern = ' *(?P<first>[A-Z][^ ]*( +[A-Z][^ ]*)*) +(?P<last>.*) *'
                    suggestion = ' and '.join([
                        person.strip() if person in WEIRD_NAMES
                        else re.sub(
                            pattern,
                            (lambda match: match.group('last') + ', ' + match.group('first')),
                            person)
                        for person in people
                    ])
                    print(f'    suggested:')
                    print(f'        {attr} = {{{suggestion}}},')
            # check for incorrectly-formed IDs
            # TODO
            # check for unquoted capitalizations
            title = paper.title
            changed = True
            while changed:
                changed = False
                if re.search('{[^{}]*}', title):
                    title = re.sub('{[^{}]*}', '', title)
                    changed = True
            for word in title.split():
                if '{' in word:
                    continue
                word = re.sub('[-/][A-Z]', '', word)
                # TODO this check fails for (eg.) {Response to {Adams and McDonnell}}
                if len(re.findall('[A-Za-z][A-Z]', word)) > 1:
                    print('unquoted title for {}: {}'.format(key, paper.title))
                    break

    def toc(self, out_path=None):
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
        coauthors = defaultdict(set)
        for key, paper in self.papers.items():
            authors = paper.author.split(' and ')
            for author1 in authors:
                for author2 in authors:
                    author2 = re.sub('[^A-Za-z, ]', '', author2)
                    coauthors[author1].add((author2, key))
        for author, coauth in sorted(coauthors.items()):
            coauth = sorted(coauth)
            printed = False
            for author1, author2 in zip(coauth[:-1], coauth[1:]):
                if author1[0] != author2[0] and author2[0].startswith(author1[0].strip('.')):
                    if not printed:
                        print(author)
                        printed = True
                    print('   ', author1)
                    print('   ', author2)

    def search(self, *terms):
        """Search for a paper."""
        raise NotImplementedError()

    # remote management

    def url(self, name):
        if name.endswith('.pdf'):
            name = name[:-4]
        print(_get_url(name))

    def diff(self):
        """List papers that differ between the local and remote libraries."""

        def _which_md5():
            md5_path = find_executable('md5sum')
            if md5_path:
                return [md5_path]
            md5_path = find_executable('md5')
            if md5_path:
                return [md5_path, '-r']
            raise FileNotFoundError('cannot locate md5sum or md5')

        md5_args = _which_md5()
        local_output = _run_shell_command(
            'find',
            str(self.directory),
            '-name', '*.pdf',
            '-exec', *md5_args, '{}', ';',
            capture_output=True,
            verbose=False,
        )
        remote_output = _run_shell_command(
            'ssh',
            self.remote_host,
            f"find {self.remote_path} -name '*.pdf' -exec md5sum '{{}}' ';'",
            capture_output=True,
            verbose=False,
        )
        hashes = defaultdict(dict)
        for location, output in zip(('local', 'remote'), (local_output, remote_output)):
            for line in output.stdout.decode('utf-8').splitlines():
                md5_hash, path = line.split()
                hashes[Path(path).stem][location] = md5_hash
        lines = {}
        for stem, file_hashes in hashes.items():
            if 'local' not in file_hashes:
                lines[stem] = '>'
            elif 'remote' not in file_hashes:
                lines[stem] = '<'
            elif file_hashes['local'] != file_hashes['remote']:
                lines[stem] = '!'
        for stem, symbol in sorted(lines.items()):
            print(f'{symbol} {stem}')

    def pull(self):
        """Download remote papers to the local library."""
        _run_shell_command(
            'rsync',
            '--archive',
            '--progress',
            '--rsh=ssh',
            '--exclude', '.*',
            f'{self.remote_host}:{self.remote_path}/',
            str(self.directory),
        )

    def push(self):
        """Upload local papers to the remote library."""
        _run_shell_command(
            'rsync',
            '--archive',
            '--progress',
            '--rsh=ssh',
            '--exclude', '.*',
            f'{self.directory}/',
            f'{self.remote_host}:{self.remote_path}',
        )

    def sync(self):
        """Sync the remote and local libraries.

        Equivalent to a pull, then a push.
        """
        self.pull()
        self.toc(out_path=self.directory.joinpath('index.html'))
        self.push()

    # as command line

    def __call__(self):
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


def _get_url(filepath):
    filepath = Path(filepath)
    return 'https://' + str(Path(REMOTE_HOST, 'papers', filepath.name[0].lower(), filepath.stem + '.pdf'))


def _run_shell_command(command, *args, capture_output=False, check=True, verbose=True):
    if verbose:
        print(command + ' ' + ' '.join(
            (arg if arg.startswith('-') else f'"{arg}"')
            for arg in args
        ))
    return run([command, *args], capture_output=capture_output, check=check)


def main():
    Library()()


if __name__ == '__main__':
    main()
