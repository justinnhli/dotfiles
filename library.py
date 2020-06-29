"""A library of research papers."""

import re
from pathlib import Path
from typing import Any, Optional, Dict


BIBTEX_PATH = Path('~/pim/library.bib').expanduser().resolve()
PAPERS_PATH = Path('~/papers').expanduser().resolve()
REMOTE_HOST = 'justinnhli.com'


class Paper:
    """A research paper."""

    __slots__ = [
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

    def __init__(self, paper_id):
        # type: (str) -> None
        """Initialize the Paper."""
        self.id = paper_id # pylint: disable = invalid-name
        self.type = ''

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
        return PAPERS_PATH / self.id.lower()[0] / (self.id + '.pdf')

    @property
    def remote(self):
        # type: () -> str
        """Get the URL of the remote file."""
        return 'https://' + str(Path(REMOTE_HOST, 'papers', self.id[0].lower(), self.id + '.pdf'))


class Library:
    """A Library of research Papers."""

    def __init__(self, directory=PAPERS_PATH, bibtex_path=BIBTEX_PATH):
        # type: (Path, Path) -> None
        """Initialize the Library."""
        self.directory = directory
        self.bibtex_path = bibtex_path
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
                if not line:
                    continue
                if line.startswith('@'):
                    match = re.fullmatch('@(?P<type>[^ ]+) *{(?P<id>[^,]+),', line)
                    assert match, line
                    paper = Paper(match.group('id'))
                    paper.type = match.group('type')
                elif line.startswith('}'):
                    self.papers[paper.id] = paper
                    paper = None
                else:
                    match = re.fullmatch(' *(?P<attr>[^ =]+) *= *{(?P<val>.+)},', line)
                    assert match, line
                    setattr(paper, match.group('attr'), match.group('val'))
