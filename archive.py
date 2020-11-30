#!/usr/bin/env python3
"""An archive of online articles."""

import re
from argparse import ArgumentParser
from pathlib import Path
from datetime import date as Date
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit
from typing import Optional, List, Dict

from util import filenamize, run_with_venv


try:
    from newspaper import Article as NewspaperArticle
except (ModuleNotFoundError, ImportError) as err:
    run_with_venv('pim')


ARCHIVE_PATH = Path('~/pim/archive').expanduser().resolve()

DATE_REGEX = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')


class ArticleFormatError(Exception): # noqa: D204
    """An error for badly formatted articles."""
    pass # pylint: disable = unnecessary-pass


class Article:
    """A saved online article."""

    def __init__(self, filepath):
        # type: (Path) -> None
        """Initialize the Article.

        Parameters:
            filepath (Path): The path of the Article.
        """
        self.filepath = filepath
        self.title = ''
        self.authors = [] # type: List[str]
        self.url = ''
        self.accessed = None # type: Optional[Date]
        if self.filepath.exists():
            self._read_article()

    def _read_article(self):
        # type: () -> None
        with self.filepath.open() as fd:
            self.title = fd.readline().strip()
            self.authors = [author.strip() for author in fd.readline().split(',')]
            self.url = fd.readline().strip()
            accessed = fd.readline().strip()
            if not (accessed.startswith('accessed ') and DATE_REGEX.fullmatch(accessed[-10:])):
                raise ArticleFormatError(f'failed to read {self.filepath}')
            self.accessed = Date.fromisoformat(accessed[-10:])

    @staticmethod
    def create(url):
        # type: (str) -> Article
        """Download and create an Article from an URL.

        Parameters:
            url (str): The URL to download.

        Returns:
            Article: The resulting article.
        """
        # parse article
        article = NewspaperArticle(url)
        article.download()
        article.parse()
        # create the article
        today = Date.today().isoformat()
        filepath = ARCHIVE_PATH / today / (filenamize(article.title) + '.txt')
        if not filepath.parent.exists():
            filepath.parent.mkdir()
        with filepath.open('w') as fd:
            fd.write('\n'.join([
                article.title,
                ', '.join(article.authors),
                url,
                'accessed ' + today,
            ]))
            fd.write('\n\n')
            fd.write(article.text)
        return Article(filepath)


class Archive:
    """A archive of saved Articles."""

    BAD_QUERIES = set([
        '__twitter_impression',
        'fbclid',
        'via',
    ])

    def __init__(self, directory=ARCHIVE_PATH):
        # type: (Path) -> None
        """Initialize the Archive.

        Parameters:
            directory (Path): The path of the article store.
        """
        self.directory = directory
        self.index_file = self.directory / '.index'
        self.index = {} # type: Dict[str, Article]
        self._read_index()

    def __contains__(self, url):
        # type: (str) -> bool
        return url in self.index

    def __getitem__(self, url):
        # type: (str) -> Article
        return self.index[url]

    def _read_index(self):
        # type: () -> None
        with self.index_file.open() as fd:
            for line in fd.readlines():
                url, filepath = line.strip().split('\t', maxsplit=1)
                self.index[url.strip()] = Article(Path(filepath.strip()))

    def _write_index(self):
        # type: () -> None
        with self.index_file.open('w') as fd:
            for url, article in sorted(self.index.items()):
                fd.write(f'{url}\t{article.filepath}\n')

    def _clean_url(self, url):
        # type: (str) -> str
        # pylint: disable = no-self-use
        parse = urlsplit(url)
        queries = parse_qsl(parse.query)
        queries = [
            (key, value) for key, value in queries
            if key not in self.BAD_QUERIES
        ]
        return urlunsplit((
            parse.scheme,
            parse.netloc,
            parse.path,
            urlencode(queries),
            parse.fragment,
        ))


    def add(self, url):
        # type: (str) -> Article
        """Add an article to the Archive.

        Parameters:
            url (str): The URL of the article.

        Returns:
            Article: The saved Article.
        """
        url = self._clean_url(url)
        if url not in self.index:
            self.index[url] = Article.create(url)
            self._write_index()
        return self.index[url]


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('urls', nargs='+', help='URLs of articles to archive')
    args = arg_parser.parse_args()
    archive = Archive()
    for url in args.urls:
        archive.add(url)


if __name__ == '__main__':
    main()
