#!/usr/bin/env python3
"""An adjustable, by-example web scraping module."""

import re
from argparse import ArgumentParser
from ast import literal_eval
from collections import namedtuple, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Optional, Union, Callable, Iterable, Sequence, Mapping, Dict, Set, List, Tuple
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup


EXAMPLES_FILE = Path(__file__).parent / 'scraper-examples'
EXTRACTORS_FILE = Path(__file__).parent / 'scraper-extractors'

XPath = Tuple[str, ...]
ExtractedValue = Union[str, Tuple[str, ...]]

class Example:

    def __init__(self, url, items):
        # type: (str, Mapping[str, Any]) -> None
        self.url = url
        self.items = items

    def __getitem__(self, key):
        return self.items[key]


ItemMatch = namedtuple('ItemMatch', 'expected, xpath, text, distance')

ExampleExtractions = namedtuple('ExampleExtractions', 'example, soup, matches')


class ItemExtractor:

    def __init__(self, attr, xpath, postprocessor_str):
        # type: (str, XPath, ...], str) -> None
        self.attr = attr
        self.xpath = xpath
        self.postprocessor_str = postprocessor_str
        # pylint: disable = eval-used
        self.postprocessor = eval(self.postprocessor_str) # type: Callable[[str], ExtractedValue]

    @property
    def literal_evalable(self):
        # type: () -> Tuple[str, Xpath, str]
        return (self.attr, self.xpath, self.postprocessor_str)

    @staticmethod
    def create_interactively(item, extractions):
        # type: (str, List[ExampleExtractions]) -> ItemExtractor
        """Create an item extractor interactively."""
        print(item)
        print()
        xpath, matches = find_best_xpath_match(item, extractions)
        print('    ' + ' / '.join(xpath) + f' ({xpath_to_selector(xpath)})')
        print()
        postprocessor_str = '(lambda text: text)'
        postprocessor = eval(postprocessor_str) # pylint: disable = eval-used
        all_matches = all(match.text == match.expected for match in matches)
        while not all_matches:
            for match in matches:
                print(f'        expected: {match.expected}')
                print(f'        actual: {postprocessor(match.text)}')
                print()
            try:
                postprocessor_str = input('    postprocessor? ')
                print()
                postprocessor = eval(postprocessor_str) # pylint: disable = eval-used
                all_matches = all(postprocessor(match.text) == match.expected for match in matches)
            except (KeyboardInterrupt, SystemExit): # pylint: disable = try-except-raise
                raise
            except Exception as err: # pylint: disable = broad-except
                postprocessor_str = '(lambda text: text)'
                postprocessor = eval(postprocessor_str) # pylint: disable = eval-used
                all_matches = all(postprocessor(match.text) == match.expected for match in matches)
                print('    ' + str(err))
                print()
        return ItemExtractor(item, xpath, postprocessor_str)


class Extractor:
    """An information extractor for a domain."""

    def __init__(self, domain, item_extractors=None):
        # type: (str, Iterable[ItemExtractor]) -> None
        if item_extractors is None:
            item_extractors = []
        self.domain = domain
        self._extractors = {} # type: Dict[str, ItemExtractor]
        for item_extractor in item_extractors:
            self._extractors[item_extractor.attr] = item_extractor

    def __getitem__(self, key):
        # type: (str) -> Optional[ItemExtractor]
        return self._extractors.get(key, None)

    @property
    def literal_evalable(self):
        # type: () -> Tuple[str, Tuple[Tuple[str, XPath, str], ...]]
        return (
            self.domain,
            tuple(
                item_extractor.literal_evalable
                for item_extractor in self._extractors.values()
            ),
        )

    def add_item(self, attr, xpath, preprocessor_str):
        # type: (str, XPath, str) -> None
        self._extractors[attr] = ItemExtractor(attr, xpath, preprocessor_str)

    def _get_xpath_text(self, element, xpath):
        # type: (BeautifulSoup, Iterable[str]) -> str
        # pylint: disable = no-self-use
        for part in xpath:
            if part.startswith('#'):
                element = element.find(id=part[1:])
            elif '[' in part:
                match = re.fullmatch(r'(?P<tag>[a-z]+)\[(?P<n>[0-9]+)\]', part)
                assert match is not None
                index = int(match.group('n')) - 1
                tags = element.find_all(match.group('tag'), recursive=False)
                if len(tags) <= index:
                    return ''
                element = element.find_all(match.group('tag'), recursive=False)[index]
            else:
                element = element.find_all(part, recursive=False)[0]
            if element is None:
                return ''
        return extract_text(element)

    def extract(self, url_or_soup):
        # type: (Union[str, BeautifulSoup]) -> Dict[str, ExtractedValue]
        # TODO check that URL fits domain
        if isinstance(url_or_soup, str):
            soup = make_soup(url_or_soup)
        else:
            soup = url_or_soup
        return {
            attr: extractor.postprocessor(self._get_xpath_text(soup, extractor.xpath))
            for attr, extractor in self._extractors.items()
        }

    def update(self, examples):
        # type: (Iterable[Example]) -> None
        extracted = []
        for example in examples:
            soup = make_soup(example.url)
            matches = self.extract(soup)
            extracted.append(ExampleExtractions(example, soup, matches))
        mismatched_attrs = set() # type: Set[str]
        for extraction in extracted:
            mismatched_attrs = mismatched_attrs.union(
                attr for attr, val in extraction.example.items.items()
                if extraction.matches.get(attr, None) != val
            )
        for attr in mismatched_attrs:
            self._extractors[attr] = ItemExtractor.create_interactively(attr, extracted)

    @staticmethod
    def from_literal_eval(literal):
        # type: (Tuple[str, Tuple[Tuple[str, XPath, str], ...]]) -> Extractor
        extractor = Extractor(literal[0])
        for attr, path, postprocessor in literal[1]:
            extractor.add_item(attr, path, postprocessor)
        return extractor


# parsing


def make_soup(url):
    # type: (str) -> BeautifulSoup
    """Create a BeautifulSoup from the URL."""
    path = Path('cache-' + re.sub('[^a-z0-9]', '', url, flags=re.IGNORECASE))
    if not path.exists():
        response = requests.get(url)
        if response.status_code != 200:
            raise IOError(f'Unable to download {url} (status code {response.status_code})')
        html = response.text
        with path.open('w') as fd:
            fd.write(html)
    with path.open() as fd:
        html = fd.read()
    return BeautifulSoup(html, 'html.parser')


def extract_text(element):
    # type: (BeautifulSoup) -> str
    """Extract all text from the BeautifulSoup element."""
    text = []
    for desc in element.descendants:
        if not hasattr(desc, 'contents'):
            if desc.strip():
                text.append(desc.strip())
    return re.sub(r'  \+', ' ', ''.join(text).strip())


def element_to_xpath(element):
    # type: (BeautifulSoup) -> XPath
    """Convert a BeautifulSoup element to a tuple of xpath components.

    Taken from https://gist.github.com/ergoithz/6cf043e3fdedd1b94fcf
    """

    def get_segment(element):
        # type: (BeautifulSoup) -> str
        """Convert an element to its xpath segment."""
        result = element.name
        siblings = element.parent.find_all(element.name, recursive=False)
        if len(siblings) > 1:
            result += '['
            result += str(next(i for i, s in enumerate(siblings, 1) if s is element))
            result += ']'
        return result

    if element.name:
        child = element
    else:
        child = element.parent
    components = []
    for parent in child.parents:
        if child.get('id', '').strip():
            components.append(f'#{child["id"]}')
            break
        components.append(get_segment(child))
        child = parent
    return tuple(reversed(components))


def xpath_to_selector(xpath):
    # type: (XPath) -> str
    """Convert an xpath to a CSS selector."""
    pattern = r'(?P<tag>[a-z]+)\[(?P<n>[0-9]+)\]'
    replacement = r'\g<tag>:nth-child(\g<n>)'
    parts = []
    for part in xpath:
        if '[' in part:
            parts.append(re.sub(pattern, replacement, part))
        else:
            parts.append(part)
    return ' '.join(parts)


# storage and retrieval


def read_examples():
    # type: () -> Dict[str, List[Example]]
    """Read stored examples."""
    with EXAMPLES_FILE.open() as fd:
        literal_examples = literal_eval(fd.read())
    examples = defaultdict(list) # type: Dict[str, List[Example]]
    for url, items in literal_examples:
        examples[urlsplit(url).netloc].append(Example(url, items))
    return examples


def read_extractors():
    # type: () -> Dict[str, Extractor]
    """Read stored Extractors."""
    if not EXTRACTORS_FILE.exists():
        return {}
    with EXTRACTORS_FILE.open() as fd:
        literal_extractors = literal_eval(fd.read())
    results = {} # type: Dict[str, Extractor]
    for domain, literal_item_extractors in literal_extractors:
        extractor = Extractor(domain)
        for attr, xpath, postprocessor_str in literal_item_extractors:
            extractor.add_item(attr, xpath, postprocessor_str)
        results[domain] = extractor
    return results


# updating


def find_best_xpath_match(item, extractions):
    # type: (str, Sequence[ExampleExtractions]) -> Tuple[XPath, Set[ItemMatch]]
    # find all xpaths for all extractions
    xpath_matches = defaultdict(set) # type: Dict[XPath, Set[ItemMatch]]
    for extraction in extractions:
        needle = extraction.example[item]
        if isinstance(needle, str):
            needles = tuple([needle])
        else:
            needles = tuple(needle)
            needle = tuple(needle)
        pins = [needle.replace(' ', '') for needle in needles]
        pins_len = sum(len(pin) for pin in pins)
        for element in extraction.soup.find_all():
            text = extract_text(element)
            compressed_text = text.replace(' ', '')
            if all(pin in compressed_text for pin in pins):
                match = ItemMatch(
                    needle,
                    element_to_xpath(element),
                    text,
                    len(compressed_text) - pins_len,
                )
                xpath_matches[match.xpath].add(match)
    # remove paths that don't work for all examples
    xpath_matches = {
        xpath: matches
        for xpath, matches in xpath_matches.items()
        if len(matches) == len(extractions)
    }
    # if no xpath works for all examples, give up
    if not xpath_matches:
        raise ValueError(f'failed to find matches for {item}')
    # sort xpaths by length, across all examples
    xpath, matches = min(
        xpath_matches.items(),
        key=(lambda pair: (mean(match.distance for match in pair[1]), -len(pair[0]))),
    )
    return xpath, matches


def update_extractors():
    # type: () -> None
    examples = read_examples()
    extractors = read_extractors()
    for domain, domain_examples in examples.items():
        if domain not in extractors:
            extractors[domain] = Extractor(domain)
        extractors[domain].update(domain_examples)
    with EXTRACTORS_FILE.open('w') as fd:
        fd.write('{\n')
        for _, extractor in sorted(extractors.items()):
            domain, item_extractors = extractor.literal_evalable
            fd.write(f'    ({repr(domain)}, (\n')
            for item_extractor in item_extractors:
                fd.write(f'        {repr(item_extractor)},\n')
            fd.write(f'    )),\n')
        fd.write('}\n')


# extraction


def extract(url):
    # type: (str) -> Dict[str, ExtractedValue]
    extractors = read_extractors()
    domain = urlsplit(url).netloc
    if domain not in extractors:
        raise ValueError(f'no extractor defined for {domain}')
    return extractors[domain].extract(url)


def main():
    # type: () -> None
    arg_parser = ArgumentParser()
    arg_parser.add_argument('args', nargs='+', metavar='arg')
    args = arg_parser.parse_args()
    if any(arg == 'update' for arg in args.args):
        if len(args.args) == 1:
            update_extractors()
        else:
            arg_parser.error('arguments must be "update" or multiple URLs')
    else:
        for url in args.args:
            extract(url)


if __name__ == '__main__':
    main()
