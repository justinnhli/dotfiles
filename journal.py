#!/usr/bin/env python3
"""Command line tool for viewing and maintaining a journal."""

import re
from argparse import ArgumentParser, Namespace, _ArgumentGroup
from ast import literal_eval
from calendar import monthrange
from collections import namedtuple, defaultdict
from copy import copy
from datetime import datetime, timedelta
from inspect import currentframe
from itertools import chain, groupby, product
from os import chdir as cd, chmod, environ, execvp, fork, remove as rm, wait
from pathlib import Path
from stat import S_IRUSR
from statistics import mean, median, stdev
from sys import stdout, exit as sys_exit
from tarfile import open as open_tar_file, TarInfo
from tempfile import mkstemp
from textwrap import dedent
from typing import Any, Optional, Union, Callable, Generator, Iterable, Sequence, Mapping

Entry = namedtuple('Entry', 'title, text, filepath, line_num')

JOURNAL_PATH = Path('~/pim/journal').expanduser().resolve()

FILE_EXTENSION = '.journal'
STRING_LENGTHS = {
    'year': 4,
    'month': 7,
    'day': 10,
}
DATE_LENGTH = STRING_LENGTHS['day']

REFERENCE_REGEX = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
DATE_REGEX = re.compile(REFERENCE_REGEX.pattern + '(, (Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day)?')
RANGE_BOUND_REGEX = re.compile('([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?')
RANGE_REGEX = re.compile(RANGE_BOUND_REGEX.pattern + ':?' + RANGE_BOUND_REGEX.pattern)


class Journal:
    """A journal."""

    def __init__(self, directory, use_cache=True, ignores=None):
        # type: (Path, bool, Optional[set[Path]]) -> None
        """Initialize the journal.

        Parameters:
            directory (Path): The directory of the journal.
            use_cache (bool): Whether to use the cache file. Defaults to True.
            ignores (Iterable[Path]): Paths to ignore. Optional.
        """
        self.directory = directory.expanduser().resolve()
        if ignores is None:
            self.ignores = set()
        else:
            self.ignores = set(ignores)
        self.entries = {} # type: dict[str, Entry]
        if use_cache:
            self._check_metadata()
            self._read_cache()
        else:
            for journal_file in self.journal_files:
                self._read_file(journal_file)

    def __len__(self):
        # type: () -> int
        return len(self.entries)

    def __getitem__(self, key):
        # type: (str) -> Entry
        return self.entries[key]

    @property
    def journal_files(self):
        # type: () -> Generator[Path, None, None]
        """Get files associated with this Journal.

        Yields:
            Path: Journal files.
        """
        for journal_file in self.directory.glob('**/*.journal'):
            if journal_file in self.ignores:
                continue
            yield journal_file

    @property
    def tags_file(self):
        # type: () -> Path
        """Get the tag file associated with this Journal.

        Returns:
            Path: The tag file.
        """
        return self.directory.joinpath('.tags').resolve()

    @property
    def cache_file(self):
        # type: () -> Path
        """Get the cache file associated with this Journal.

        Returns:
            Path: The cache file.
        """
        return self.directory.joinpath('.cache').resolve()

    def _check_metadata(self):
        # type: () -> None
        metadata_files = (
            self.tags_file,
            self.cache_file,
        )
        if not all(metadata_file.exists() for metadata_file in metadata_files):
            self.update_metadata()

    def _read_file(self, filepath):
        # type: (Path) -> None
        with filepath.open() as fd:
            line_num = 1
            for raw_entry in fd.read().strip().split('\n\n'):
                lines = raw_entry.splitlines()
                title = lines[0]
                self.entries[title] = Entry(
                    title,
                    raw_entry,
                    filepath,
                    line_num,
                )
                line_num += len(lines) + 1

    def _read_cache(self):
        # type: () -> None
        with self.cache_file.open() as fd:
            for title, entry_dict in literal_eval(fd.read()).items():
                self.entries[title] = Entry(
                    title,
                    entry_dict['text'],
                    Path(entry_dict['filepath']).expanduser().resolve(),
                    entry_dict['line_num'],
                )

    def _filter_by_terms(self, selected, terms, icase):
        # type: (set[str], Iterable[str], bool) -> set[str]
        flags = re.MULTILINE
        if icase:
            flags |= re.IGNORECASE
        for term in terms:
            if icase:
                term = term.lower()
            matches = set(
                title for title, entry in self.entries.items()
                if re.search(term, entry.text, flags=flags)
            )
            selected &= matches
        return selected

    def _filter_by_date(self, selected, *date_ranges):
        # type: (set[str], tuple[str, Optional[str]]) -> set[str]
        # pylint: disable = no-self-use
        first_date = min(selected)
        last_date = next_date(max(selected))
        candidates = copy(selected)
        selected = set()
        for date_range in date_ranges:
            start_date, end_date = date_range
            start_date, end_date = (start_date or first_date, end_date or last_date)
            selected |= set(k for k in candidates if start_date <= k < end_date)
        return selected

    def filter(self, terms=None, date_ranges=None, icase=True):
        # type: (Iterable[str], Sequence[tuple[str, Optional[str]]], bool) -> dict[str, Entry]
        """Filter the entries.

        Parameters:
            terms (Iterable[str]): Search terms for the entries.
            date_ranges (Sequence[tuple[str, Optional[str]]]):
                Date ranges for the entries. Optional.
            icase (bool): Ignore case. Defaults to True.

        Returns:
            Dict[str, Entry]: The entries.
        """
        selected = set(self.entries.keys())
        if date_ranges:
            selected = self._filter_by_date(
                set(
                    title for title in selected
                    if REFERENCE_REGEX.match(title)
                ),
                *date_ranges,
            )
        if terms:
            selected = self._filter_by_terms(selected, terms, icase)
        return {title: self.entries[title] for title in selected}

    def _write_tags_file(self):
        # type: () -> None
        tags = {}
        for journal_file in self.journal_files:
            self._read_file(journal_file)
            rel_path = journal_file.relative_to(self.directory)
            with journal_file.open() as fd:
                for line_num, line in enumerate(fd, start=1):
                    if not line or line.startswith('\t'):
                        continue
                    line = line.strip()
                    tags[line] = (rel_path, line_num)
                    if DATE_REGEX.fullmatch(line.rstrip()):
                        tags[line[:DATE_LENGTH]] = (rel_path, line_num)
        with self.tags_file.open('w') as fd:
            for tag, (filepath, line_num) in sorted(tags.items()):
                fd.write(f'{tag}\t{filepath}\t{line_num}\n')

    def _write_cache(self):
        # type: () -> None
        with self.cache_file.open('w') as fd:
            fd.write('{\n')
            for entry in sorted(self.entries.values()):
                fd.write(dedent(f'''
                    '{entry.title}': {{
                        'title': '{entry.title}',
                        'filepath': '{entry.filepath.relative_to(self.directory)}',
                        'line_num': {entry.line_num},
                        'text': {repr(entry.text)},
                    }},
                ''').strip())
                fd.write('\n')
            fd.write('}\n')

    def lint(self):
        # type: () -> list[tuple[Path, int, str]]
        """Check the journal for errors."""
        # pylint: disable = line-too-long, too-many-nested-blocks, too-many-branches
        errors = []
        titles = set()
        long_dates = None
        for journal_file in self.journal_files:
            has_date_stem = RANGE_BOUND_REGEX.fullmatch(journal_file.stem)
            with journal_file.open() as fd:
                lines = fd.read().splitlines()
            if not lines:
                journal_file.unlink()
                continue
            if lines[0].startswith('\ufeff'):
                errors.append((journal_file, 1, 'byte order mark'))
            elif lines[0].strip() == '':
                errors.append((journal_file, 1, 'file starts on blank line'))
            if lines[-1].strip() == '':
                errors.append((journal_file, len(lines), 'file ends on blank line'))
            prev_indent = 0
            prev_line = ''
            for line_num, line in enumerate(lines, start=1): # pylint: disable = unused-variable
                indent = len(re.match('\t*', line)[0])
                if not re.fullmatch('(\t*([^ \t][ -~]*)?[^ \t])?', line):
                    errors.append(log_error('non-tab indentation, trailing whitespace, or non-ASCII character'))
                line = line.strip()
                if not line.startswith('|') and '  ' in line:
                    errors.append(log_error('multiple spaces'))
                if indent == 0:
                    if line:
                        if prev_indent != 0 or prev_line != '':
                            errors.append(log_error('no blank line between entries'))
                        if DATE_REGEX.fullmatch(line):
                            if long_dates is None:
                                long_dates = (len(line) > DATE_LENGTH)
                            elif long_dates != (len(line) > DATE_LENGTH):
                                errors.append(log_error('inconsistent date format'))
                            if not title_to_date(line).strftime('%Y-%m-%d, %A').startswith(line):
                                errors.append(log_error('date-weekday correctness'))
                            if has_date_stem and not line.startswith(journal_file.stem):
                                errors.append(log_error("filename doesn't match entry"))
                        if line in titles:
                            errors.append(log_error('duplicate titles'))
                        titles.add(line)
                    elif prev_indent == 0:
                        errors.append(log_error('consecutive unindented lines'))
                        print('here')
                elif indent - prev_indent > 1:
                    errors.append(log_error('unexpected indentation'))
                prev_indent = indent
                prev_line = line
        return sorted(errors)

    def update_metadata(self):
        # type: () -> list[tuple[Path, int, str]]
        """Update the tags file and the cache."""
        errors = self.lint()
        if not errors:
            self._write_tags_file()
            self._write_cache()
        return errors


# utility functions


def title_to_date(title):
    # type: (str) -> datetime
    """Convert an entry title to a datetime.

    Parameters:
        title (str): The entry title.

    Returns:
        datetime: The datetime.
    """
    if DATE_REGEX.fullmatch(title):
        return datetime.strptime(title[:DATE_LENGTH], '%Y-%m-%d')
    else:
        return datetime.today()


def next_date(date_or_str):
    # type: (Union[datetime, str]) -> str
    """Calculate the next date.

    Parameters:
        date_or_str (Union[datetime, str]): The previous date.

    Returns:
        str: The next date.
    """
    if isinstance(date_or_str, str):
        date = title_to_date(date_or_str)
    else:
        date = date_or_str
    return (date + timedelta(days=1)).strftime('%Y-%m-%d')


def filter_entries(journal, args, **kwargs):
    # type: (Journal, Namespace, Any) -> dict[str, Entry]
    """Filter entries by the CLI arguments.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
        **kwargs: Override values for the CLI arguments.

    Returns:
        Dict[str, Entry]: The entries.
    """
    return journal.filter(
        terms=kwargs.get('terms', args.terms),
        date_ranges=kwargs.get('date_ranges', args.date_ranges),
        icase=kwargs.get('icase', args.icase),
    )


def group_entries(entries, args):
    # type: (Mapping[str, Entry], Namespace) -> chain[tuple[str, Iterable[str]]]
    """Group entries by date.

    Parameters:
        entries (Mapping[str, Entry]): The entries.
        args (Namespace): The CLI arguments.

    Returns:
        Iterator[tuple[str, Iterable[str]]]: The grouped entries.
    """
    unit_length = STRING_LENGTHS[args.unit]
    return chain(
        groupby(
            sorted(entries.keys(), reverse=args.reverse),
            (lambda k: k[:unit_length] if DATE_REGEX.fullmatch(k) else 'other'),
        ),
        [('all', tuple(entries.keys()))],
    )


def print_table(data, headers=None, gap_size=2):
    # type: (list[Sequence[str]], Sequence[str], int) -> None
    """Print a table of data.

    Parameters:
        data (List[Sequence[str]]): The rows of data.
        headers (Sequence[str]): The headers. Optional.
        gap_size (int): The number of spaces between columns. Defaults to 2.
    """
    rows = data
    if headers is not None:
        rows = [headers] + rows
    widths = [max(len(row[col]) for row in rows) for col in range(len(data[0]))]
    gap = gap_size * ' '
    if headers:
        print(gap.join(col.center(width) for width, col in zip(widths, headers)))
        print(gap.join(width * '-' for width in widths))
    for row in data:
        print(gap.join(col.rjust(width) for width, col in zip(widths, row)))


def log_error(message):
    # type: (str) -> tuple[Path, int, str]
    """Create the log error message.

    Parameters:
        message (str): The error message.

    Returns:
        Path: The journal file where the error occurred.
        int: The line where the error occurred.
        str: The error message.
    """
    local_vars = currentframe().f_back.f_locals
    return (
        local_vars['journal_file'],
        local_vars['line_num'],
        message,
    )


# operations

OPERATIONS = []
Option = namedtuple('Option', 'priority, flag, desc, function')


def register(*args):
    # type: (str) -> Callable[[Callable[[Journal, Namespace], None]], Callable[[Journal, Namespace], None]]
    """Register a function for the CLI.

    Parameters:
        *args (str): The option and the description.

    Returns:
        Callable[[Callable[[Journal, Namespace], None]], Callable[[Journal, Namespace], None]]:
            The argument function.
    """
    def wrapped(function):
        # type: (Callable[[Journal, Namespace], None]) -> Callable[[Journal, Namespace], None]
        assert 1 <= len(args) <= 2
        assert function.__name__.startswith('do_')
        if len(args) == 1:
            priority = 2
            flag = '--' + function.__name__[3:].replace("_", "-")
            desc = args[0]
        elif len(args) == 2:
            priority = 1
            flag, desc = args
        OPERATIONS.append(Option(priority, flag, desc, function))
        return function

    return wrapped


@register('-A', 'archive to datetimed tarball')
def do_archive(_, args):
    # type: (Journal, Namespace) -> None
    """Archive to datetimed tarball.

    Parameters:
        args (Namespace): The CLI arguments.
    """
    from os.path import basename, join as join_path # pylint: disable = import-outside-toplevel

    def tarinfo_filter(tarinfo):
        # type: (TarInfo) -> Optional[TarInfo]
        if basename(tarinfo.name)[0] in '._':
            return None
        elif tarinfo.size > 1048576:
            return None
        else:
            return tarinfo

    archive_name = 'jrnl' + datetime.now().strftime('%Y%m%d%H%M%S')
    with open_tar_file(archive_name + '.txz', 'w:xz') as tar:
        tar.add(args.directory, arcname=archive_name, filter=tarinfo_filter)
        tar.add(__file__, arcname=join_path(archive_name, basename(__file__)))


@register('-C', 'count words and entries')
def do_count(journal, args):
    # type: (Journal, Namespace) -> None
    """Count words and entries.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    COLUMNS = { # pylint: disable = invalid-name
        'DATE': (lambda journal, unit, titles, num_words: unit),
        'POSTS': (lambda journal, unit, titles, num_words: len(titles)),
        'FREQ': (lambda journal, unit, titles, num_words:
            f'{((title_to_date(max(titles)) - title_to_date(min(titles))).days + 1) / len(titles):.2f}'
        ),
        'SIZE': (lambda journal, unit, titles, num_words:
            f'{sum(len(journal[date].text) for date in titles):,d}'
        ),
        'WORDS': (lambda journal, unit, titles, num_words: f'{sum(num_words):,d}'),
        'MIN': (lambda journal, unit, titles, num_words: min(num_words)),
        'MED': (lambda journal, unit, titles, num_words: round(median(num_words))),
        'MAX': (lambda journal, unit, titles, num_words: max(num_words)),
        'MEAN': (lambda journal, unit, titles, num_words: round(mean(num_words))),
        'STDEV': (lambda journal, unit, titles, num_words:
            0 if len(num_words) <= 1 else round(stdev(num_words))
        ),
    } # type: dict[str, Callable[[Mapping[str, Entry], str, Sequence[str], Sequence[int]], Any]]

    entries = filter_entries(journal, args)
    if not entries:
        return
    length_map = {date: len(entry.text.split()) for date, entry in entries.items()}
    grouped_entries = group_entries(entries, args)
    table = [] # type: list[Sequence[str]]
    for timespan, titles in grouped_entries:
        titles = tuple(titles)
        lengths = tuple(length_map[title] for title in titles)
        table.append([
            str(func(journal, timespan, titles, lengths))
            for column, func in COLUMNS.items()
        ])
    if args.headers:
        headers = tuple(COLUMNS.keys())
    else:
        headers = None
    print_table(table, headers=headers)


@register('-G', 'graph entry references in DOT')
def do_graph(journal, args):
    # type: (Journal, Namespace) -> None
    """Graph entry references in DOT.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    entries = filter_entries(journal, args)
    entries = {
        title[:DATE_LENGTH]:entry for title, entry
        in entries.items() if DATE_REGEX.fullmatch(title)
    }
    disjoint_sets = dict((k, k) for k in entries)
    referents = defaultdict(set) # type: dict[str, set[str]]
    edges = defaultdict(set) # type: dict[str, set[str]]
    for src, entry in sorted(entries.items()):
        dests = set(
            dest for dest in REFERENCE_REGEX.findall(entry.text)
            if src > dest and dest in entries
        )
        referents[src].update(*(referents[dest] for dest in dests))
        for dest in dests - referents[src]:
            edges[src].add(dest)
            while disjoint_sets[dest] != src:
                disjoint_sets[dest], dest = src, disjoint_sets[dest]
        referents[src] |= dests
    components = defaultdict(set) # type: dict[str, set[str]]
    for rep in disjoint_sets:
        path = set([rep])
        while disjoint_sets[rep] != rep:
            path.add(rep)
            rep = disjoint_sets[rep]
        components[rep] |= path
    print('digraph {')
    print('\tgraph [size="48", model="subset", rankdir="BT"];')
    print('\tnode [fontcolor="#4E9A06", shape="none"];')
    print('\tedge [color="#555753"];')
    print('')
    for srcs in sorted(components.values(), key=(lambda s: (len(s), min(s))), reverse=True):
        print(f'\t// component size = {len(srcs)}')
        node_lines = defaultdict(set)
        edge_lines = set()
        for src in srcs:
            node_lines[src[:STRING_LENGTHS['month']]].add(
                f'"{src}" [fontsize="{len(entries[src].text.split()) / 100}"];'
            )
            for dest in edges[src]:
                edge_lines.add(f'"{src}" -> "{dest}";')
        for _, entry_lines in sorted(node_lines.items(), reverse=args.reverse):
            print('\tsubgraph {')
            print('\t\trank="same";')
            for entry_line in sorted(entry_lines, reverse=args.reverse):
                print('\t\t' + entry_line)
            print('\t}')
        for edge_line in sorted(edge_lines, reverse=args.reverse):
            print('\t' + edge_line)
        print('')
    print('}')


@register('-I', 're-index and update cache')
def do_index(journal, _):
    # type: (Journal, Namespace) -> None
    """Re-index and update cache.

    Parameters:
        journal (Journal): The journal.
    """
    errors = journal.update_metadata()
    if errors:
        print('\n'.join('{}:{}: {}'.format(*error) for error in errors))
        sys_exit(1)


@register('-L', 'list entry titles')
def do_list(journal, args):
    # type: (Journal, Namespace) -> None
    """List entry titles.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    entries = filter_entries(journal, args)
    print('\n'.join(sorted(entries.keys(), reverse=args.reverse)))


@register('-S', 'show entry contents')
def do_show(journal, args):
    # type: (Journal, Namespace) -> None
    """Show entry contents.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    entries = filter_entries(journal, args)
    if not entries:
        return
    text = '\n\n'.join(entry.text for _, entry in sorted(entries.items(), reverse=args.reverse))
    if stdout.isatty():
        temp_file = Path(mkstemp(FILE_EXTENSION)[1]).expanduser().resolve()
        with temp_file.open('w') as fd:
            fd.write(text)
        chmod(temp_file, S_IRUSR)
        if fork():
            wait()
            rm(temp_file)
        else:
            cd(args.directory)
            editor = environ.get('VISUAL', environ.get('EDITOR', 'nvim'))
            vim_args = [editor, str(temp_file), '-c', f'cd {args.directory}', '-c', 'set hlsearch nospell']
            if args.terms:
                vim_args[-1] += ' ' + ('nosmartcase' if args.icase else 'noignorecase')
                vim_args.extend((
                    '-c',
                    r'let @/="\\v' + '|'.join(
                        f'({term})' for term in args.terms
                    ).replace('"', r'\"').replace('@', r'\\@') + '"',
                ))
            execvp(editor, vim_args)
    else:
        print(text)


@register('list entries that hyphenate the terms differently')
def do_hyphenation(journal, args):
    # type: (Journal, Namespace) -> None
    """List entries that hyphenate the terms differently.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    for puncts in product(['', ' ', '-'], repeat=(len(args.terms) - 1)):
        possibility = ''.join(
            part + punct for part, punct
            in zip(args.terms, puncts)
        ) + args.terms[-1]
        entries = filter_entries(journal, args, terms=[possibility])
        print(possibility)
        for title in sorted(entries, reverse=args.reverse):
            print('    ' + title)


@register('list the length of the longest line of each entry')
def do_lengths(journal, args):
    # type: (Journal, Namespace) -> None
    """List the length of the longest line of each entry.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    entries = filter_entries(journal, args)
    for title, entry in sorted(entries.items()):
        print(title, max(len(line) for line in entry.text.splitlines()))


@register('list the Kincaid reading grade level of each entry')
def do_readability(journal, args):
    # type: (Journal, Namespace) -> None
    """List the Kincaid reading grade level of each entry.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """

    def to_sentences(text):
        # type: (str) -> chain[str]
        for paragraph in text.splitlines():
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            sentences = chain(*(sentence.split('! ') for sentence in paragraph.split('. ')))
            sentences = chain(*(sentence.split('? ') for sentence in sentences))
            yield from sentences

    def strip_punct(text):
        # type: (str) -> str
        text = text.replace("'", '')
        text = re.sub('[^ 0-9A-Za-z]', ' ', text)
        text = re.sub(' +', ' ', text)
        return text.strip()

    def letters_to_syllables(letters, rate):
        # type: (int, float) -> float
        return letters / rate

    def kincaid(text):
        # type: (str) -> float
        sentences = [strip_punct(sentence) for sentence in to_sentences(text)]
        num_letters = sum(len(word) for sentence in sentences for word in sentence)
        num_words = sum(len(sentence.split()) for sentence in sentences)
        num_sentences = len(sentences)
        return (
            0.39 * (num_words / num_sentences)
            + 11.8 * (letters_to_syllables(num_letters, 4.10) / num_words)
            - 15.59
        )

    entries = filter_entries(journal, args)
    if not entries:
        return
    table = [] # type: list[Sequence[str]]
    for timespan, titles in group_entries(entries, args):
        text = '\n'.join(journal[title].text for title in titles)
        table.append((timespan, f'{kincaid(text): >6.3f}'))
    print_table(table, headers=['ENTRY', 'KINCAID'])


@register('list search results in vim :grep format')
def do_vimgrep(journal, args):
    # type: (Journal, Namespace) -> None
    """List search results in vim :grep format.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    prefix_len = 20
    suffix_len = 40
    entries = filter_entries(journal, args)
    if not args.terms:
        args.terms.append('^.')
    # TODO sort results for non-date titles
    for _, entry in sorted(entries.items(), reverse=args.reverse):
        lines = entry.text.splitlines()
        results = []
        for term in args.terms:
            for match in re.finditer(term, entry.text, flags=args.icase):
                match_index = match.start()
                if match_index == 0:
                    line_num = 1
                    col_num = 1
                else:
                    prev_lines = entry.text[:match_index].splitlines()
                    line_num = len(prev_lines)
                    col_num = len(prev_lines[-1]) + 1
                match_line = lines[line_num - 1].strip()
                if col_num < prefix_len:
                    start_index = 0
                    prefix = ''
                else:
                    start_index = match_line.rfind(' ', 0, col_num - prefix_len) + 1
                    prefix = '[...] '
                if col_num > len(match_line) - suffix_len:
                    end_index = len(match_line)
                    suffix = ''
                else:
                    end_index = match_line.find(' ', col_num + len(match.group()) + suffix_len)
                    suffix = ' [...]'
                snippet = match_line[start_index:end_index]
                results.append((line_num, col_num, f'{prefix}{snippet}{suffix}'))
        for line_num, col_num, preview in sorted(results):
            print(f'{entry.filepath}:{entry.line_num + line_num - 1}:{col_num}: {preview}')


# CLI


def build_arg_parser(arg_parser):
    # type: (ArgumentParser) -> ArgumentParser
    """Add arguments to the ArgumentParser.

    Parameters:
        arg_parser (ArgumentParser): The argument parser.

    Returns:
        ArgumentParser: The argument parser.

    """
    arg_parser.usage = '%(prog)s <operation> [options] [TERM ...]'
    arg_parser.description = 'A command line tool for viewing and maintaining a journal.'
    arg_parser.add_argument(
        'terms',
        metavar='TERM',
        nargs='*',
        help='pattern which must exist in entries',
    )

    group = None # type: Optional[_ArgumentGroup]
    group = arg_parser.add_argument_group('OPERATIONS').add_mutually_exclusive_group(required=True)
    for _, flag, desc, function in sorted(OPERATIONS, key=(lambda option: (option.priority, option.flag))):
        group.add_argument(
            flag,
            dest='operation',
            action='store_const',
            const=function,
            help=desc,
        )

    group = arg_parser.add_argument_group('INPUT OPTIONS')
    group.add_argument(
        '--directory',
        dest='directory',
        action='store',
        type=Path,
        default=Path.cwd(),
        help='use journal files in directory',
    )
    group.add_argument(
        '--ignore',
        dest='ignores',
        action='append',
        type=Path,
        default=[],
        help='ignore specified file',
    )
    group.add_argument(
        '--skip-cache',
        dest='use_cache',
        action='store_false',
        help='skip cached entries and indices',
    )

    group = arg_parser.add_argument_group('FILTER OPTIONS (IGNORED BY -[AI])')
    group.add_argument(
        '-d',
        dest='date_spec',
        action='store',
        help='only use entries in date range',
    )
    group.add_argument(
        '-i',
        dest='icase',
        action='store_false',
        default=re.IGNORECASE,
        help='ignore case-insensitivity',
    )

    group = arg_parser.add_argument_group('OUTPUT OPTIONS (IGNORED BY -[AI])')
    group.add_argument(
        '-c',
        dest='reverse',
        action='store_false',
        help='list entries in chronological order',
    )

    group = arg_parser.add_argument_group('OPERATION-SPECIFIC OPTIONS')
    group.add_argument(
        '--no-headers',
        dest='headers',
        action='store_false',
        help='[C] do not print headers',
    )
    group.add_argument(
        '--unit',
        dest='unit',
        action='store',
        choices=('year', 'month', 'day'),
        default='year',
        help='[C] set tabulation unit (default: year)',
    )

    group = arg_parser.add_argument_group('MISCELLANEOUS OPTIONS')
    group.add_argument(
        '--no-log',
        dest='log',
        action='store_false',
        help='do not log filter',
    )

    return arg_parser


def fill_date_range(date_range):
    # type: (str) -> tuple[Optional[str], Optional[str]]
    """Expand date ranges to start and end dates.

    Parameters:
        date_range (str): The CLI date range.

    Returns:
        str: The start date.
        str: The end date.
    """
    if ':' in date_range:
        start_date, end_date = date_range.split(':')
    else:
        start_date = date_range
        if len(date_range) == 4:
            end_date = str(int(date_range) + 1)
        else:
            units = [int(unit) for unit in date_range.split('-')]
            if len(units) == 2:
                units.append(monthrange(*units)[1])
            end_date = next_date(datetime(*units))
    if start_date:
        start_date = start_date + '-01' * int((DATE_LENGTH - len(start_date)) / len('-01'))
    else:
        start_date = None
    if end_date:
        end_date = end_date + '-01' * int((DATE_LENGTH - len(end_date)) / len('-01'))
    else:
        end_date = None
    return (start_date, end_date)


def process_args(arg_parser, args):
    # type: (ArgumentParser, Namespace) -> Namespace
    """Process and check CLI arguments.

    Parameters:
        arg_parser (ArgumentParser): The CLI argument parser.
        args (Namespace): The CLI arguments.

    Returns:
        Namespace: The CLI arguments, augmented.
    """
    if args.operation.__name__ == 'do_hyphenation':
        args.terms = list(chain(*(term.split('-') for term in args.terms)))
        if len(args.terms) < 2:
            arg_parser.error('argument --hyphenation: two or more terms required')
    if args.date_spec is None:
        args.date_ranges = None
    else:
        date_ranges = []
        for date_range in args.date_spec.split(','):
            if not (date_range and RANGE_REGEX.fullmatch(date_range)):
                arg_parser.error(
                    f'argument -d: "{date_range}" should be in format '
                    '[YYYY[-MM[-DD]]][:][YYYY[-MM[-DD]]][,...]'
                )
            date_ranges.append(fill_date_range(date_range))
        args.date_ranges = date_ranges
    args.directory = args.directory.expanduser().resolve()
    args.ignores = set(path.expanduser().resolve() for path in args.ignores)
    return args


def parse_args(arg_parser, args):
    # type: (ArgumentParser, Namespace) -> None
    """Parser the CLI arguments.

    Parameters:
        arg_parser (ArgumentParser): The CLI argument parser.
        args (Namespace): The CLI arguments.
    """
    if arg_parser is None:
        arg_parser = build_arg_parser(ArgumentParser())
    args = process_args(arg_parser, args)
    journal = Journal(args.directory, use_cache=args.use_cache, ignores=args.ignores)
    if len(journal) == 0:
        arg_parser.error(f'no journal entries found in {args.directory}')
    if args.log:
        log_search(arg_parser, args, journal)
    args.operation(journal, args)


def log_search(arg_parser, args, journal):
    # type: (ArgumentParser, Namespace, Journal) -> None
    """Log a Journal search.

    Parameters:
        arg_parser (ArgumentParser): The CLI argument parser.
        args (Namespace): The CLI arguments.
        journal (Journal): The journal.
    """
    # pylint: disable = protected-access
    logged_functions = ('do_show', 'do_list', 'do_vimgrep')
    if args.operation.__name__ not in logged_functions:
        return
    log_file = journal.directory.joinpath('.log').resolve()
    if not (args.log and log_file.exists()):
        return
    options = [] # type: list[tuple[str, Optional[str]]]
    for option_string, option in arg_parser._option_string_actions.items():
        if args.operation is option.const:
            op_flag = option_string
        elif re.fullmatch('-[a-gi-z]', option_string):
            option_value = getattr(args, option.dest)
            if option_value != option.default:
                if option.const in (True, False):
                    options.append((option_string, None))
                else:
                    options.append((option_string, option_value))
    log_args = op_flag
    collapsible = (len(op_flag) == 2)
    for opt_str, opt_val in sorted(options, key=(lambda x: (len(x) != 1, x[0].upper()))):
        log_args += f' {opt_str} {opt_val}'
        if opt_val is None and collapsible:
            log_args = log_args.lstrip(' -')
        collapsible = (len(opt_str) == 2 and opt_val is None)
    terms = ' '.join(
        '"{}"'.format(term.replace('"', '\\"'))
        for term in sorted(args.terms)
    ).strip()
    with log_file.open('a') as fd:
        fd.write(f'{datetime.today().isoformat(" ")}\t{log_args} -- {terms}\n')


def main():
    # type: () -> None
    """Provide CLI entry point."""
    arg_parser = build_arg_parser(ArgumentParser())
    args = arg_parser.parse_args()
    parse_args(arg_parser, args)


if __name__ == '__main__':
    main()
