#!/usr/bin/env python3
"""Command line tool for viewing and maintaining a journal."""

# pylint: disable = too-many-lines

import re
from json import load as json_read, dump as json_write
from argparse import ArgumentParser, Namespace, _ArgumentGroup
from calendar import monthrange
from collections import namedtuple, defaultdict
from datetime import datetime, timedelta
from inspect import currentframe
from itertools import chain, groupby
from os import chdir as cd, chmod, environ, execvp, fork, wait
from pathlib import Path
from stat import S_IRUSR
from statistics import mean, median, stdev
from sys import stdout, exit as sys_exit
from tarfile import open as open_tar_file, TarInfo
from tempfile import mkstemp
from typing import Any, Optional, Union, Callable, Generator, Iterable, Sequence, Mapping

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


class Title:
    """A utility class for handling date and non-date titles."""

    def __init__(self, title):
        # type: (str) -> None
        """Initialize a new Title."""
        self.title = title
        self.is_date = bool(DATE_REGEX.fullmatch(self.title))
        self._date = None # type: Optional[datetime]
        self._iso = None # type: Optional[str]

    @property
    def date(self):
        # type: () -> datetime
        """Get the date represented by the title."""
        assert self.is_date
        if self._date is None:
            self._date = datetime.strptime(self.title[:DATE_LENGTH], '%Y-%m-%d')
        return self._date

    def iso(self, unit='day', default=None):
        # type: (str, Optional[str]) -> str
        """Get a normalized title.

        Parameters:
            unit (str): The unit of the date. One of 'year', 'month', or 'day'.
            default (str): The default title, if the title is not a date.
        """
        if self._iso is None:
            if self.is_date:
                self._iso = self.date.strftime('%Y-%m-%d')[:STRING_LENGTHS['day']]
            else:
                self._iso = self.title
        if self.is_date:
            return self._iso[:STRING_LENGTHS[unit]]
        elif default is not None:
            return default
        else:
            return self._iso

    def __lt__(self, other):
        # type: (Title) -> bool
        return self.iso() < other.iso()

    def __eq__(self, other):
        # type: (Any) -> bool
        return self.iso() == other.iso()

    def __hash__(self):
        # type: () -> int
        return hash(self.iso())

    def __str__(self):
        # type: () -> str
        return self.title


Entry = namedtuple('Entry', 'title, text, filepath, line_num')
Entries = Mapping[Title, Entry]
DateRange = tuple[Optional[datetime], Optional[datetime]]


class Journal(Entries):
    """A journal."""

    def __init__(self, directory, use_cache=True, ignores=None):
        # type: (Union[Path, str], bool,  Optional[set[Path]]) -> None
        """Initialize the journal.

        Parameters:
            directory (Union[Path, str]): The directory of the journal.
            use_cache (bool): Whether to use the cache file. Defaults to True.
            ignores (Iterable[Path]): Paths to ignore. Optional.
        """
        if isinstance(directory, str):
            directory = Path(directory)
        self.directory = directory.expanduser().resolve()
        if ignores is None:
            self.ignores = set()
        else:
            self.ignores = set(ignores)
        self.entries = {} # type: dict[Title, Entry]
        if use_cache:
            self._check_metadata()
            self._read_cache()
        else:
            for journal_file in self.journal_files:
                self._read_file(journal_file)

    def __len__(self):
        # type: () -> int
        return len(self.entries)

    def __iter__(self):
        # type: () -> Generator[Title, None, None]
        yield from sorted(self.entries)

    def __getitem__(self, key):
        # type: (Title) -> Entry
        return self.entries[key]

    @property
    def journal_files(self):
        # type: () -> Generator[Path, None, None]
        """Get files associated with this Journal.

        Yields:
            Path: Journal files.
        """
        for journal_file in self.directory.glob(f'**/*{FILE_EXTENSION}'):
            if journal_file in self.ignores:
                continue
            if any(part.startswith('.') for part in journal_file.relative_to(self.directory).parts):
                continue
            yield journal_file

    @property
    def tags_file(self):
        # type: () -> Path
        """Get the tag file associated with this Journal.

        Returns:
            Path: The tag file.
        """
        return self.directory / '.tags'

    @property
    def cache_file(self):
        # type: () -> Path
        """Get the cache file associated with this Journal.

        Returns:
            Path: The cache file.
        """
        return self.directory / '.cache'

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
                title = Title(lines[0])
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
            for title, entry_dict in json_read(fd).items():
                title = Title(title)
                self.entries[title] = Entry(
                    title,
                    entry_dict['text'],
                    self.directory / entry_dict['rel_path'],
                    entry_dict['line_num'],
                )

    def _filter_by_terms(self, selected, terms, icase, whole_words):
        # type: (set[Title], Iterable[str], bool, bool) -> set[Title]
        flags = re.MULTILINE
        if icase:
            flags |= re.IGNORECASE
        for term in terms:
            if whole_words:
                term = r'\b' + term + r'\b'
            selected = set(
                title for title in selected
                if re.search(term, self.entries[title].text, flags=flags)
            )
        return selected

    def _filter_by_date(self, selected, *date_ranges):
        # type: (set[Title], DateRange) -> set[Title]
        first_date = min(selected).date
        last_date = next_date(max(selected).date)
        candidates = set()
        for date_range in date_ranges:
            start_date, end_date = date_range
            start_date, end_date = (start_date or first_date, end_date or last_date)
            candidates |= set(k for k in selected if start_date <= k.date < end_date)
        return candidates

    def filter(self, terms=None, icase=True, whole_words=False, date_ranges=None, dates_only=False):
        # type: (Iterable[str], bool, bool, Sequence[DateRange], bool) -> dict[Title, Entry]
        """Filter the entries.

        Parameters:
            terms (Iterable[str]): Search terms for the entries.
            icase (bool): Ignore case. Defaults to True.
            whole_words (bool): Match must be the entire word. Defaults to False.
            date_ranges (Sequence[DateRange]):
                Date ranges for the entries. Optional.
            dates_only (bool): Filter out non-date entries.

        Returns:
            dict[str, Entry]: The entries.
        """
        selected = set(self.entries.keys())
        if date_ranges or dates_only:
            selected = set(title for title in selected if title.is_date)
        if date_ranges:
            selected = self._filter_by_date(selected, *date_ranges)
        if terms:
            selected = self._filter_by_terms(selected, terms, icase, whole_words)
        return {title: self.entries[title] for title in selected}

    def _write_tags_file(self):
        # type: () -> None
        tags = []
        for title, entry in sorted(self.entries.items()):
            filepath = entry.filepath.relative_to(self.directory)
            if DATE_REGEX.fullmatch(title.title) and title.title != title.title[:10]:
                tags.append(f'{title.title[:10]}\t{filepath}\t{entry.line_num}')
            tags.append(f'{title.title}\t{filepath}\t{entry.line_num}')
        with self.tags_file.open('w', encoding='utf-8') as fd:
            fd.write('\n'.join(tags))

    def _write_cache(self):
        # type: () -> None
        entries = {
            str(title): {
                'title': str(title),
                'rel_path': str(entry.filepath.relative_to(self.directory)),
                'line_num': entry.line_num,
                'text': entry.text,
            }
            for title, entry in self.entries.items()
        }
        with self.cache_file.open('w', encoding='utf-8') as fd:
            json_write(entries, fd)

    def lint(self):
        # type: () -> list[tuple[Path, int, str]]
        """Check the journal for errors."""
        # pylint: disable = too-many-nested-blocks, too-many-branches
        ascii_regex = re.compile('(\t*[!-~]([ -~]*[!-~])?)?')
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
                if not ascii_regex.fullmatch(line):
                    errors.append(log_error(
                        'non-tab indentation, trailing whitespace, or non-ASCII character'
                    ))
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


def next_date(date):
    # type: (datetime) -> datetime
    """Calculate the next date.

    Parameters:
        date (datetime): The previous date.

    Returns:
        datetime: The next date.
    """
    return date + timedelta(days=1)


def filter_entries(journal, args, **kwargs):
    # type: (Journal, Namespace, Any) -> dict[Title, Entry]
    """Filter entries by the CLI arguments.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
        **kwargs: Override values for the CLI arguments.

    Returns:
        dict[str, Entry]: The entries.
    """
    return journal.filter(
        terms=kwargs.get('terms', args.terms),
        icase=kwargs.get('icase', args.icase),
        whole_words=kwargs.get('whole_words', args.whole_words),
        date_ranges=kwargs.get('date_ranges', args.date_ranges),
        dates_only=kwargs.get('dates_only', None),
    )


def group_entries(entries, unit, summary=True, reverse=True):
    # type: (Entries, str, bool, bool) -> dict[str, Entries]
    """Group entries by date.

    Parameters:
        entries (Entries): The entries.
        unit (str): The tabulation unit. One of 'year', 'month', or 'day'.
        summary (bool): Whether to show a summary. Defaults to True.
        reverse (bool): Whether to show entries in chronological order.
            Defaults to True.

    Returns:
        dict[str, Entries]: The grouped entries.
    """

    def key_func(entry):
        # type: (tuple[Title, Entry]) -> str
        return entry[0].iso(unit, 'other')

    grouped = groupby(
        sorted(entries.items(), reverse=reverse, key=key_func),
        key_func,
    )
    result = {group: dict(entries) for group, entries in grouped} # type: dict[str, Entries]
    if summary:
        result['all'] = entries
    return result


def print_table(data, headers=None, gap_size=2):
    # type: (list[Sequence[Any]], Optional[Sequence[str]], int) -> None
    """Print a table of data.

    Parameters:
        data (list[Sequence[Any]]): The rows of data.
        headers (Optional[Sequence[str]]): The headers.
        gap_size (int): The number of spaces between columns. Defaults to 2.
    """
    if not data:
        return
    rows = [[str(datum) for datum in row] for row in data] # type: list[Sequence[str]]
    if headers:
        rows = [headers] + rows
    widths = [max(len(row[col]) for row in rows) for col in range(len(rows[0]))]
    gap = gap_size * ' '
    if headers:
        print(gap.join(col.center(width) for width, col in zip(widths, headers)))
        print(gap.join(width * '-' for width in widths))
        rows = rows[1:]
    for row in rows:
        print(gap.join(col.rjust(width) for width, col in zip(widths, row)))


def summarize_line_lengths(entries, unit, num_words):
    # type: (Entries, str, Sequence[int]) -> str
    # pylint: disable = unused-argument
    """Get the length of the longest line of a group of entries.

    Parameters:
        entries (Entries): The entries.
        unit (str): The grouping unit.
        num_words (Sequence[int]): The number of words in each entry in the group.

    Returns:
        str: The length of longest line.
    """
    text = '\n'.join(entry.text for entry in entries.values())
    return str(max(len(line) for line in text.splitlines()))


def summarize_readability(entries, unit, num_words):
    # type: (Entries, str, Sequence[int]) -> str
    # pylint: disable = unused-argument
    """Calculate the Kincaid reading grade level of a group of entries.

    Parameters:
        entries (Entries): The entries.
        unit (str): The grouping unit.
        num_words (Sequence[int]): The number of words in each entry in the group.

    Returns:
        str: The reading grade level.
    """
    non_alnum_regex = re.compile('[^ 0-9A-Za-z]')
    multispace_regex = re.compile('  +')

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
        text = non_alnum_regex.sub(' ', text)
        text = multispace_regex.sub(' ', text)
        return text.strip()

    def letters_to_syllables(letters):
        # type: (int) -> float
        return letters / 3.26 # constant updated 2021-07-14

    def kincaid(text):
        # type: (str) -> float
        sentences = [strip_punct(sentence) for sentence in to_sentences(text)]
        words = strip_punct(text).split()
        num_letters = sum(len(word) for word in words)
        num_words = len(words)
        num_sentences = len(sentences)
        return (
            0.39 * (num_words / num_sentences)
            + 11.8 * (letters_to_syllables(num_letters) / num_words)
            - 15.59
        )

    text = '\n'.join(entry.text for entry in entries.values())
    return f'{kincaid(text):.3f}'


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
    frame = currentframe()
    assert frame, 'Python does not support frame introspection'
    frame = frame.f_back
    journal_file = None
    line_num = None
    while True:
        local_vars = frame.f_locals
        if 'journal_file' in local_vars and 'line_num' in local_vars:
            journal_file = local_vars['journal_file'],
            line_num = local_vars['line_num'],
            break
        frame = frame.f_back
    return (journal_file, line_num, message)


# operations

OPERATIONS = []
Option = namedtuple('Option', 'priority, flag, desc, function')
COUNT_COL_FNS = {
    'LINE LEN': ('length', summarize_line_lengths),
    'READABILITY': ('readability', summarize_readability),
}
GRAPH_NODE_FNS = {
    'uniform': (lambda entries, node: 48),
    'length': (lambda entries, node: len(entries[node].text.split()) / 100),
    'cites': (lambda entries, node:
        5 * (1 + sum(
            1 for entry in entries.values()
            if entry.text > node and node in entry.text
        ))
    ),
    'refs': (lambda entries, node: 5 * len(REFERENCE_REGEX.findall(entries[node].text))),
}


def register(flag=None):
    # type: (str) -> Callable[[Callable[[Journal, Namespace], None]], Callable[[Journal, Namespace], None]]
    """Register a function for the CLI.

    Parameters:
        flag (str): The option flag. Optional; if not provided, the function name is used instead.

    Returns:
        Callable[[Callable[[Journal, Namespace], None]], Callable[[Journal, Namespace], None]]:
            The argument function.
    """

    def wrapped(function, flag):
        # type: (Callable[[Journal, Namespace], None], str) -> Callable[[Journal, Namespace], None]
        assert function.__name__.startswith('do_')
        if flag is None:
            priority = 2
            flag = '--' + function.__name__[3:].replace("_", "-")
        else:
            priority = 1
        desc = function.__doc__.splitlines()[0].strip('.')
        desc = desc[0].lower() + desc[1:]
        OPERATIONS.append(Option(priority, flag, desc, function))
        return function

    return (lambda function: wrapped(function, flag)) # pylint: disable = superfluous-parens


@register('-A')
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


@register('-C')
def do_count(journal, args):
    # type: (Journal, Namespace) -> None
    """Count words and entries.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    columns = {
        'DATE': (lambda entries, unit, num_words: unit),
        'POSTS': (lambda entries, unit, num_words: len(entries)),
        'FREQ': (lambda entries, unit, num_words:
            f'{((max(entries).date - min(entries).date).days + 1) / len(entries):.2f}'
        ),
        'SIZE': (lambda entries, unit, num_words:
            f'{sum(len(entries[date].text) for date in entries):,d}'
        ),
        'WORDS': (lambda entries, unit, num_words: f'{sum(num_words):,d}'),
        'MIN': (lambda entries, unit, num_words: min(num_words)),
        'MED': (lambda entries, unit, num_words: round(median(num_words))),
        'MAX': (lambda entries, unit, num_words: max(num_words)),
        'MEAN': (lambda entries, unit, num_words: round(mean(num_words))),
        'STDEV': (lambda entries, unit, num_words:
            0 if len(num_words) <= 1 else round(stdev(num_words))
        ),
    } # type: dict[str, Callable[[Entries, str, Sequence[int]], Any]]
    for heading, (flag, function) in COUNT_COL_FNS.items():
        if flag in args.columns:
            columns[heading] = function
    entries = filter_entries(journal, args, dates_only=True)
    if not entries:
        return
    length_map = {title: len(entry.text.split()) for title, entry in entries.items()}
    table = [] # type: list[Sequence[str]]
    for timespan, group in group_entries(entries, args.unit, args.summary, args.reverse).items():
        lengths = tuple(length_map[title] for title in group)
        table.append([func(group, timespan, lengths) for column, func in columns.items()])
    print_table(table, (list(columns.keys()) if args.headers else []))


@register('-G')
def do_graph(journal, args):
    # type: (Journal, Namespace) -> None
    """Graph entry references in DOT.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    entries = filter_entries(journal, args, dates_only=True)
    disjoint_sets = dict((k, k) for k in entries)
    referents = defaultdict(set) # type: dict[Title, set[Title]]
    edges = defaultdict(set) # type: dict[Title, set[Title]]
    for src, entry in sorted(entries.items()):
        dests = set(Title(dest) for dest in REFERENCE_REGEX.findall(entry.text))
        dests = set(
            dest for dest in dests
            if src > dest and dest in entries
        )
        referents[src].update(*(referents[dest] for dest in dests))
        outgoing_edges = dests
        if args.simplify_edges:
            outgoing_edges -= referents[src]
        for dest in outgoing_edges:
            edges[src].add(dest)
            while disjoint_sets[dest] != src:
                disjoint_sets[dest], dest = src, disjoint_sets[dest]
        referents[src] |= dests
    components = defaultdict(set) # type: dict[Title, set[Title]]
    for rep in disjoint_sets:
        path = set([rep])
        while disjoint_sets[rep] != rep:
            path.add(rep)
            rep = disjoint_sets[rep]
        components[rep] |= path
    node_fn = GRAPH_NODE_FNS[args.node_size] # type: Callable[[Entries, Title], float]
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
            node_lines[src.iso()].add(
                f'"{src.iso()}" [fontsize="{node_fn(entries, src)}"];'
            )
            for dest in edges[src]:
                edge_lines.add(f'"{src.iso()}" -> "{dest.iso()}";')
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


@register('-I')
def do_index(journal, _):
    # type: (Journal, Namespace) -> None
    """Re-index and update cache.

    Parameters:
        journal (Journal): The journal.
    """
    errors = journal.update_metadata()
    if errors:
        print('\n'.join(f'{path}:{line}: {message}' for path, line, message in errors))
        sys_exit(1)


@register('-L')
def do_list(journal, args):
    # type: (Journal, Namespace) -> None
    """List entry titles.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    entries = filter_entries(journal, args)
    print('\n'.join(
        str(title) for title
        in sorted(entries.keys(), reverse=args.reverse)
    ))


@register('-S')
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
        with temp_file.open('w', encoding='utf-8') as fd:
            fd.write(text)
        chmod(temp_file, S_IRUSR)
        if fork():
            wait()
            temp_file.unlink()
        else:
            cd(args.directory)
            editor = environ.get('VISUAL', environ.get('EDITOR', 'nvim'))
            vim_args = [
                editor,
                str(temp_file),
                '-c', f'cd {args.directory}',
                '-c', 'set hlsearch nospell',
            ]
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


@register('-W')
def do_wording(journal, args):
    # type: (Journal, Namespace) -> None
    """Count uses of a phrase.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    journal_text = '\n'.join(
        entry.text for entry in
        filter_entries(journal, args, terms=None).values()
    )
    alpha_regex = re.compile("[a-z']", flags=re.IGNORECASE)
    if args.terms:
        phrases = set(['-'.join(args.terms),])
    else:
        hyphen_regex = re.compile("([a-z']+(-[a-z']+)+)", flags=re.IGNORECASE)
        phrases = set(matches[0] for matches in hyphen_regex.finditer(journal_text))
    matches = set(chain(*(
        re.finditer(r'[ -]?'.join(phrase.split('-')), journal_text, flags=re.IGNORECASE)
        for phrase in sorted(phrases)
    )))
    seen = set()
    rows = []
    for match in matches:
        variant = match.group()
        if args.icase:
            variant = variant.lower()
        if variant in seen:
            continue
        seen.add(variant)
        if args.whole_words:
            if alpha_regex.match(journal_text[match.start() - 1]):
                continue
            if alpha_regex.match(journal_text[match.end()]):
                continue
            term = r'\b' + re.escape(match.group()) + r'\b'
        else:
            term = re.escape(match.group())
        entries = filter_entries(journal, args, terms=[term])
        rows.append((variant, len(entries), min(entries).iso(), max(entries).iso()))
    print_table(
        sorted(rows, key=(lambda row: row[1])),
        ['VARIANT', 'COUNT', 'FIRST', 'LAST'],
    )


@register()
def do_vimgrep(journal, args):
    # type: (Journal, Namespace) -> None
    """List results in vim :grep format.

    Parameters:
        journal (Journal): The journal.
        args (Namespace): The CLI arguments.
    """
    prefix_words = 3
    suffix_words = 8
    entries = filter_entries(journal, args)
    if not args.terms:
        args.terms.append('^.')
    for _, entry in sorted(entries.items(), reverse=args.reverse):
        lines = entry.text.splitlines()
        results = []
        for term in args.terms:
            for match in re.finditer(term, entry.text, flags=args.icase):
                prev_lines = ('\n' + entry.text[:match.start() + 1]).splitlines()
                line_num = len(prev_lines) - 1
                col_num = len(prev_lines[-1]) - 1
                match_line = lines[line_num - 1]
                prefix = re.search(
                    r'(\S+ ){,' + str(prefix_words) + r'}\S*$',
                    match_line[:col_num],
                ).group()
                suffix = re.search(
                    r'^\S*( \S+){,' + str(suffix_words) + '}',
                    match_line[col_num + len(match.group()):],
                ).group()
                results.append((line_num, col_num + 1, f'{prefix}{match.group()}{suffix}'))
        for line_num, col_num, preview in sorted(results):
            print(':'.join([
                f'{entry.filepath}',
                f'{entry.line_num + line_num - 1}',
                f'{col_num}',
                f' {preview}',
            ]))


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
    for _, flag, desc, function in sorted(OPERATIONS, key=(lambda opt: (opt.priority, opt.flag))):
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
    group.add_argument(
        '-w',
        dest='whole_words',
        action='store_true',
        help='only match whole words',
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
        '--no-summary',
        dest='summary',
        action='store_false',
        help='[C] do not print summary statistics',
    )
    group.add_argument(
        '--unit',
        dest='unit',
        choices=tuple(STRING_LENGTHS.keys()),
        default='year',
        help='[C] set tabulation unit (default: %(default)s)',
    )
    group.add_argument(
        '--column',
        dest='columns',
        action='append',
        choices=tuple(COUNT_COL_FNS.keys()),
        default=[],
        help='[C] include additional statistics',
    )
    group.add_argument(
        '--no-simplify-edges',
        dest='simplify_edges',
        action='store_false',
        help='[G] keep all edges',
    )
    group.add_argument(
        '--node-size-fn',
        choices=tuple(GRAPH_NODE_FNS.keys()),
        default='length',
        help='[G] the attribute that affects node size (default: %(default)s)',
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
    # type: (str) -> DateRange
    """Expand date ranges to start and end dates.

    Parameters:
        date_range (str): The CLI date range.

    Returns:
        datetime: The start date.
        datetime: The end date.
    """
    if ':' in date_range:
        start, end = date_range.split(':')
    else:
        start = date_range
        if len(date_range) == 4:
            end = str(int(date_range) + 1)
        else:
            units = [int(unit) for unit in date_range.split('-')]
            if len(units) == 2:
                units.append(monthrange(*units)[1])
            end = next_date(datetime(*units)).strftime('%Y-%m-%d') # type: ignore[arg-type]
    if start:
        start = start + '-01' * int((DATE_LENGTH - len(start)) / len('-01'))
        start_date = datetime.strptime(start, '%Y-%m-%d')
    else:
        start_date = None
    if end:
        end = end + '-01' * int((DATE_LENGTH - len(end)) / len('-01'))
        end_date = datetime.strptime(end, '%Y-%m-%d')
    else:
        end_date = None
    if start_date is not None and end_date is not None and start_date > end_date:
        return (None, None)
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
    if args.operation.__name__ == 'do_wording':
        args.terms = list(chain(*(term.split('-') for term in args.terms)))
    elif args.operation.__name__ == 'do_index':
        args.use_cache = False
    if args.date_spec is None:
        args.date_ranges = None
    else:
        range_regex = re.compile(RANGE_BOUND_REGEX.pattern + ':?' + RANGE_BOUND_REGEX.pattern)
        date_ranges = []
        for date_range in args.date_spec.split(','):
            if not (len(date_range) > 1 and range_regex.fullmatch(date_range)):
                arg_parser.error(
                    f'argument -d: "{date_range}" should be in format '
                    '[YYYY[-MM[-DD]]][:][YYYY[-MM[-DD]]][,...]'
                )
            start_date, end_date = fill_date_range(date_range)
            if start_date is end_date is None:
                arg_parser.error(
                    f'argument -d: "{date_range}" has a start date after the end date'
                )
            date_ranges.append((start_date, end_date))
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
    try:
        stdout.flush()
    except BrokenPipeError:
        pass


def log_search(arg_parser, args, journal):
    # type: (ArgumentParser, Namespace, Journal) -> None
    # pylint: disable = protected-access
    """Log a Journal search.

    Parameters:
        arg_parser (ArgumentParser): The CLI argument parser.
        args (Namespace): The CLI arguments.
        journal (Journal): The journal.
    """
    logged_functions = ('do_show', 'do_list', 'do_vimgrep')
    if args.operation.__name__ not in logged_functions:
        return
    log_file = journal.directory / '.log'
    if not (args.log and log_file.exists()):
        return
    op_flag = None
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
    for opt_str, opt_val in sorted(options, key=(lambda pair: (pair[1] is not None, pair[0].upper()))):
        if collapsible and len(opt_str) == 2:
            log_args += opt_str[1]
        else:
            log_args += f' {opt_str}'
        if opt_val is not None:
            log_args += f' {opt_val}'
        collapsible = (len(opt_str) == 2 and opt_val is None)
    terms = ' '.join(
        '"{}"'.format(term.replace('"', '\\"'))
        for term in sorted(args.terms)
    ).strip()
    with log_file.open('a') as fd:
        fd.write(f'{datetime.today().isoformat(" ")}\t{log_args} -- {terms}\n')


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    arg_parser = build_arg_parser(ArgumentParser())
    args = arg_parser.parse_args()
    parse_args(arg_parser, args)


if __name__ == '__main__':
    main()
