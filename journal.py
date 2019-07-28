#!/usr/bin/env python3

import re
import tarfile
from argparse import ArgumentParser
from collections import namedtuple, defaultdict
from copy import copy
from datetime import datetime, timedelta
from heapq import nlargest, nsmallest
from inspect import currentframe
from itertools import chain, groupby, product
from os import chdir as cd, chmod, environ, execvp, fork, remove as rm, wait
from pathlib import Path
from stat import S_IRUSR
from statistics import mean, median, stdev
from sys import stdout
from tempfile import mkstemp

Entry = namedtuple('Entry', 'date, text, filepath')

FILE_EXTENSION = '.journal'
STRING_LENGTHS = {
    'year': 4,
    'month': 7,
    'day': 10,
}
DATE_LENGTH = STRING_LENGTHS['day']
DATE_REGEX = re.compile(
    '([0-9]{4}-[0-9]{2}-[0-9]{2})'
    '(, (Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day)?'
)
RANGE_REGEX = re.compile(
    '([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?'
    ':?'
    '([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?'
)
REF_REGEX = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')


class Journal:

    def __init__(self, directory, use_cache=True, ignores=None):
        self.directory = directory
        if ignores is None:
            ignores = set()
        self.ignores = ignores
        self.entries = {}
        if use_cache:
            self._check_cache_files()
            self._read_file(self.cache_file)
        else:
            for journal_file in self.journal_files:
                self._read_file(journal_file)

    def __getitem__(self, key):
        return self.entries[key]

    @property
    def journal_files(self):
        for journal_file in self.directory.glob('**/*.journal'):
            if journal_file in self.ignores:
                continue
            yield journal_file

    @property
    def tags_file(self) -> Path:
        return self.directory.joinpath('.tags').resolve()

    @property
    def cache_file(self) -> Path:
        return self.directory.joinpath('.cache').resolve()

    def _check_cache_files(self):
        cache_files = (
            self.tags_file,
            self.cache_file,
        )
        if not all(cache_file.exists() for cache_file in cache_files):
            self.update_metadata()

    def _read_file(self, filepath):
        with open(filepath) as fd:
            for raw_entry in fd.read().strip().split('\n\n'):
                if DATE_REGEX.match(raw_entry):
                    entry = Entry(
                        raw_entry[:DATE_LENGTH],
                        raw_entry,
                        filepath,
                    )
                    self.entries[entry.date] = entry

    def _filter_by_terms(self, selected, terms, icase):
        flags = re.MULTILINE
        if icase:
            flags |= re.IGNORECASE
        for term in terms:
            if icase:
                term = term.lower()
            matches = set(
                date for date, entry in self.entries.items()
                if re.search(term, entry.text, flags=flags)
            )
            selected &= matches
        return selected

    def _filter_by_date(self, selected, *date_ranges):
        # pylint: disable = no-self-use
        first_date = min(selected)
        last_date = (
            datetime.strptime(max(selected), '%Y-%m-%d') + timedelta(days=1)
        ).strftime('%Y-%m-%d')
        candidates = copy(selected)
        selected = set()
        for date_range in date_ranges:
            if len(date_range) == 2:
                start_date, end_date = date_range
                start_date, end_date = (start_date or first_date, end_date or last_date)
                selected |= set(k for k in candidates if start_date <= k < end_date)
            else:
                selected |= set(k for k in candidates if k.startswith(date_range))
        return selected

    def filter(self, terms=None, date_ranges=None, icase=True):
        selected = set(self.entries.keys())
        if date_ranges:
            selected = self._filter_by_date(selected, *date_ranges)
        if terms:
            selected = self._filter_by_terms(selected, terms, icase)
        return {date: self.entries[date] for date in selected}

    def update_metadata(self):
        self.entries = {}
        tags = {}
        for journal_file in self.journal_files:
            self._read_file(journal_file)
            rel_path = journal_file.relative_to(self.directory)
            with journal_file.open() as fd:
                lines = fd.read().splitlines()
            for line_number, line in enumerate(lines, start=1):
                if DATE_REGEX.fullmatch(line):
                    tags[line[:DATE_LENGTH]] = (rel_path, line_number)
        with self.tags_file.open('w') as fd:
            for tag, (filepath, line) in sorted(tags.items()):
                fd.write('\t'.join([tag, str(filepath), str(line)]) + '\n')
        with self.cache_file.open('w') as fd:
            for entry in sorted(self.entries.values()):
                fd.write(str(entry.text) + '\n\n')

    def verify(self):
        # pylint: disable = line-too-long, too-many-nested-blocks, too-many-branches
        errors = []
        dates = set()
        long_dates = None
        for journal_file in self.journal_files:
            with journal_file.open() as fd:
                lines = fd.read().splitlines()
            if lines[-1].strip() == '':
                errors.append((journal_file, len(lines), 'file ends on blank line'))
            prev_indent = 0
            for line_number, line in enumerate(lines, start=1):
                indent = len(re.match('\t*', line).group(0))
                if not re.fullmatch('(\t*([^ \t][ -~]*)?[^ \t])?', line):
                    errors.append(log_error('non-tab indentation, ending blank, or non-ASCII character'))
                if not line.lstrip().startswith('|') and '  ' in line:
                    errors.append(log_error('multiple spaces'))
                if indent == 0:
                    if DATE_REGEX.fullmatch(line):
                        entry_date = line[:DATE_LENGTH]
                        cur_date = datetime.strptime(entry_date, '%Y-%m-%d')
                        if prev_indent != 0:
                            errors.append(log_error('no empty line between entries'))
                        if not entry_date.startswith(journal_file.stem):
                            errors.append((journal_file, line_number, "filename doesn't match entry"))
                        if long_dates is None:
                            long_dates = (len(line) > DATE_LENGTH)
                        elif long_dates != (len(line) > DATE_LENGTH):
                            errors.append(log_error('inconsistent date format'))
                        if long_dates and line != cur_date.strftime('%Y-%m-%d, %A'):
                            errors.append(log_error('date-weekday correctness'))
                        if cur_date in dates:
                            errors.append(log_error('duplicate dates'))
                        dates.add(cur_date)
                    else:
                        if line:
                            if line[0] == '\ufeff':
                                errors.append(log_error('byte order mark'))
                            else:
                                errors.append(log_error('unindented text'))
                        if prev_indent == 0:
                            errors.append(log_error('consecutive unindented lines'))
                elif indent - prev_indent > 1:
                    errors.append(log_error('unexpected indentation'))
                prev_indent = indent
        if errors:
            print('\n'.join('{}:{}: {}'.format(*error) for error in sorted(errors)))
            exit(1)


# utility functions


def filter_entries(journal, args, **kwargs):
    entries = journal.filter(
        terms=kwargs.get('terms', args.terms),
        date_ranges=kwargs.get('date_ranges', args.date_ranges),
        icase=kwargs.get('icase', args.icase),
    )
    num_results = kwargs.get('num_results', args.num_results)
    if num_results is None:
        return entries
    if kwargs.get('reverse', args.reverse):
        dates = nlargest(num_results, entries)
    else:
        dates = nsmallest(num_results, entries)
    return {date: entries[date] for date in dates}


def print_table(data, headers=None, gap_size=2):
    if headers is None:
        rows = data
    else:
        rows = [headers] + data
    widths = []
    for col in range(len(data[0])):
        widths.append(max(len(row[col]) for row in rows))
    gap = gap_size * ' '
    if headers:
        print(gap.join(col.center(widths[i]) for i, col in enumerate(headers)))
        print(gap.join(width * '-' for width in widths))
    print('\n'.join(gap.join(col.rjust(widths[i]) for i, col in enumerate(row)) for row in data))


def log_error(message):
    local_vars = currentframe().f_back.f_locals
    return (
        local_vars['journal_file'],
        local_vars['line_number'],
        message,
    )


# operations

OPERATIONS = []
Option = namedtuple('Option', 'flag, desc, function')


def register(*args):

    def wrapped(function):
        assert 1 <= len(args) <= 2
        assert function.__name__.startswith('do_')
        if len(args) == 1:
            flag = ''
            desc = args[0]
        elif len(args) == 2:
            flag, desc = args
        OPERATIONS.append(Option(flag, desc, function))
        return function

    return wrapped


@register('-A', 'archive to datetimed tarball')
def do_archive(_, args):
    from os.path import basename, join as join_path
    archive_name = 'jrnl' + datetime.now().strftime('%Y%m%d%H%M%S')
    with tarfile.open(archive_name + '.txz', 'w:xz') as tar:
        tar.add(
            args.directory,
            arcname=archive_name,
            filter=(lambda tarinfo: None if basename(tarinfo.name)[0] in '._' else tarinfo),
        )
        tar.add(__file__, arcname=join_path(archive_name, basename(__file__)))


@register('-C', 'count words and entries')
def do_count(journal, args):

    def _count_fn_date(journal, unit, dates, num_words):
        # pylint: disable = unused-argument
        return unit

    def _count_fn_posts(journal, unit, dates, num_words):
        # pylint: disable = unused-argument
        return len(dates)

    def _count_fn_freq(journal, unit, dates, num_words):
        # pylint: disable = unused-argument
        num_days = (
            datetime.strptime(max(dates), '%Y-%m-%d')
            - datetime.strptime(min(dates), '%Y-%m-%d')
        ).days
        return f'{(num_days + 1) / len(dates):.2f}'

    def _count_fn_size(journal, unit, dates, num_words):
        # pylint: disable = unused-argument
        size = sum(len(journal[date].text) for date in dates)
        return f'{size:,d}'

    def _count_fn_words(journal, unit, dates, num_words):
        # pylint: disable = unused-argument
        return f'{sum(num_words):,d}'

    def _count_fn_min(journal, unit, dates, num_words):
        # pylint: disable = unused-argument
        return min(num_words)

    def _count_fn_med(journal, unit, dates, num_words):
        # pylint: disable = unused-argument
        return round(median(num_words))

    def _count_fn_max(journal, unit, dates, num_words):
        # pylint: disable = unused-argument
        return max(num_words)

    def _count_fn_mean(journal, unit, dates, num_words):
        # pylint: disable = unused-argument
        return round(mean(num_words))

    def _count_fn_stdev(journal, unit, dates, num_words):
        # pylint: disable = unused-argument
        if len(num_words) > 1:
            return round(stdev(num_words))
        else:
            return 0

    entries = filter_entries(journal, args)
    columns = ['DATE', 'POSTS', 'FREQ', 'SIZE', 'WORDS', 'MIN', 'MED', 'MAX', 'MEAN', 'STDEV']
    unit_length = STRING_LENGTHS[args.unit]
    length_map = {date: len(entry.text.split()) for date, entry in entries.items()}
    grouped_timespans = chain(
        groupby(
            sorted(entries.keys(), reverse=args.reverse),
            (lambda k: k[:unit_length]),
        ),
        [('all', tuple(entries.keys()))],
    )
    table = []
    for timespan, selected_dates in grouped_timespans:
        selected_dates = tuple(selected_dates)
        lengths = tuple(length_map[date] for date in selected_dates)
        row = []
        for column in columns:
            func = vars()[f'_count_fn_{column.lower()}']
            row.append(str(func(journal, timespan, selected_dates, lengths)))
        table.append(row)
    print_table(table, headers=columns)


@register('-G', 'graph entry references in DOT')
def do_graph(journal, args):
    entries = filter_entries(journal, args)
    disjoint_sets = dict((k, k) for k in entries)
    ancestors = defaultdict(set)
    edges = dict((k, set()) for k in entries)
    for src in sorted(entries):
        dests = set(
            dest for dest in REF_REGEX.findall(entries[src])
            if src > dest and dest in entries
        )
        ancestors[src] = set().union(*(ancestors[parent] for parent in dests))
        for dest in dests - ancestors[src]:
            edges[src].add(dest)
            while disjoint_sets[dest] != src:
                disjoint_sets[dest], dest = src, disjoint_sets[dest]
        ancestors[src] |= dests
    components = defaultdict(set)
    for rep in disjoint_sets:
        path = set([rep])
        while disjoint_sets[rep] != rep:
            path.add(rep)
            rep = disjoint_sets[rep]
        components[rep] |= path
    print('digraph {')
    print('\tgraph [size="48", model="subset", rankdir="{}"];'.format('TB' if args.reverse else 'BT'))
    print('\tnode [fontcolor="#4E9A06", shape="none"];')
    print('\tedge [color="#555753"];')
    print('')
    for srcs in sorted(components.values(), key=(lambda s: (len(s), min(s))), reverse=(not args.reverse)):
        print('\t// component size = {}'.format(len(srcs)))
        for src in sorted(srcs, reverse=args.reverse):
            print('\t"{}" [fontsize="{}"];'.format(src, len(entries[src].split()) / 100))
            if edges[src]:
                print('\n'.join(
                    '\t"{}" -> "{}";'.format(src, dest)
                    for dest in sorted(edges[src], reverse=args.reverse)
                ))
        print('')
    print('}')


@register('-L', 'list entry dates')
def do_list(journal, args):
    entries = filter_entries(journal, args)
    print('\n'.join(sorted(entries.keys(), reverse=args.reverse)))


@register('-S', 'show entry contents')
def do_show(journal, args):
    entries = filter_entries(journal, args)
    text = '\n\n'.join(entry.text for _, entry in sorted(entries.items(), reverse=args.reverse))
    if stdout.isatty():
        temp_file = Path(mkstemp(FILE_EXTENSION)[1])
        with temp_file.open('w') as fd:
            fd.write(text)
        chmod(temp_file, S_IRUSR)
        if fork():
            wait()
            rm(temp_file)
        else:
            cd(args.directory)
            editor = environ.get('VISUAL', environ.get('EDITOR', 'nvim'))
            vim_args = [editor, temp_file, '-c', 'set hlsearch nospell']
            if args.terms:
                vim_args[-1] += ' ' + ('nosmartcase' if args.icase else 'noignorecase')
                vim_args.extend((
                    '-c',
                    r'let @/="\\v' + '|'.join(
                        '({})'.format(term) for term in args.terms
                    ).replace('"', r'\"').replace('@', r'\\@') + '"',
                ))
            execvp(editor, vim_args)
    else:
        print(text)


@register('-U', 'update tags and cache file')
def do_update(journal, _):
    journal.update_metadata()


@register('-V', 'verify journal sanity')
def do_verify(journal, _):
    journal.verify()


@register('list entries that hyphenate the terms differently')
def do_hyphenation(journal, args):
    for puncts in product(['', ' ', '-'], repeat=(len(args.terms) - 1)):
        possibility = ''.join(
            part + punct for part, punct
            in zip(args.terms, puncts)
        ) + args.terms[-1]
        entries = filter_entries(journal, args, terms=[possibility])
        print(possibility)
        for date in sorted(entries):
            print('    ' + date)


@register('list the length of the longest line of each entry')
def do_lengths(journal, args):
    entries = filter_entries(journal, args)
    for date, entry in sorted(entries.items()):
        print(date, max(len(line) for line in entry.text.splitlines()))


@register('list the Kincaid reading grade level of each entry')
def do_readability(journal, args):

    def to_sentences(text):
        for paragraph in text.splitlines():
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            sentences = paragraph.split('. ')
            sentences = chain(*(sentence.split('! ') for sentence in sentences))
            sentences = chain(*(sentence.split('? ') for sentence in sentences))
            for sentence in sentences:
                if len(sentence.split()) > 2:
                    yield sentence

    def strip_punct(text):
        text = text.replace(' - ', ' ')
        text = text.replace("'", '')
        text = re.sub('([0-9A-Za-z])-([0-9A-Za-z])', r'\1 \2', text)
        text = re.sub('[^ 0-9A-Za-z]', '', text)
        return text

    def letters_to_syllables(letters, rate):
        return letters / rate

    def kincaid(text):
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
    for date, entry in sorted(entries.items()):
        print(date, '{: >6.3f}'.format(kincaid(entry.text)))


# CLI


def make_arg_parser():
    arg_parser = ArgumentParser(
        usage='%(prog)s <operation> [options] [TERM ...]',
        description='A command line tool for viewing and maintaining a journal.',
    )
    arg_parser.set_defaults(directory='./', ignores=[], icase=re.IGNORECASE, terms=[], unit='year')
    arg_parser.add_argument(
        'terms',
        metavar='TERM',
        nargs='*',
        help='pattern which must exist in entries',
    )

    group = arg_parser.add_argument_group('OPERATIONS').add_mutually_exclusive_group(required=True)
    for flag, desc, function in sorted(OPERATIONS):
        if flag:
            group.add_argument(
                flag,
                dest='operation',
                action='store_const',
                const=function,
                help=desc,
            )
    for flag, desc, function in sorted(OPERATIONS, key=(lambda option: option.function.__name__)):
        if not flag:
            flag = '--' + function.__name__[3:].replace("_", "-")
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
        help='use journal files in directory',
    )
    group.add_argument(
        '--ignore',
        dest='ignores',
        action='append',
        type=Path,
        help='ignore specified file',
    )
    group.add_argument(
        '--skip-cache',
        dest='use_cache',
        action='store_false',
        help='skip cached entries and indices',
    )

    group = arg_parser.add_argument_group('FILTER OPTIONS (IGNORED BY -[AUV])')
    group.add_argument(
        '-d',
        dest='date_spec',
        action='store',
        help='only use entries in range',
    )
    group.add_argument(
        '-i',
        dest='icase',
        action='store_false',
        help='ignore case-insensitivity',
    )
    group.add_argument(
        '-n',
        dest='num_results',
        action='store',
        type=int,
        help='limit number of results',
    )

    group = arg_parser.add_argument_group('OUTPUT OPTIONS')
    group.add_argument(
        '-r',
        dest='reverse',
        action='store_true',
        help='reverse chronological order',
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
        help='[C] set tabulation unit',
    )

    group = arg_parser.add_argument_group('MISCELLANEOUS OPTIONS')
    group.add_argument(
        '--no-log',
        dest='log',
        action='store_false',
        help='do not log filter',
    )

    return arg_parser


def parse_args(arg_parser):
    args = arg_parser.parse_args()
    if args.date_spec is None:
        args.date_ranges = None
    else:
        date_ranges = []
        for date_range in args.date_spec.split(','):
            if not (date_range and RANGE_REGEX.fullmatch(date_range)):
                arg_parser.error(
                    f'argument -d: "{args.date_range}" should be in format '
                    '[YYYY[-MM[-DD]]][:][YYYY[-MM[-DD]]][,...]'
                )
            if ':' in date_range:
                start_date, end_date = date_range.split(':')
                if start_date:
                    start_date = start_date + '-01' * int((DATE_LENGTH - len(start_date)) / len('-01'))
                else:
                    start_date = None
                if end_date:
                    end_date = end_date + '-01' * int((DATE_LENGTH - len(end_date)) / len('-01'))
                else:
                    end_date = None
                date_ranges.append((start_date, end_date))
            else:
                date_ranges.append(date_range)
        args.date_ranges = date_ranges
    if args.num_results is not None and args.num_results < 1:
        arg_parser.error('argument -n: "{}" should be a positive integer'.format(args.num_results))
    args.directory = args.directory.resolve()
    args.ignores = set(path.resolve() for path in args.ignores)
    return args


def log_search(arg_parser, args, journal):
    # pylint: disable = protected-access
    if args.operation.__name__[3:] not in ('show', 'list'):
        return
    log_file = journal.directory.joinpath('.log').resolve()
    if args.log and log_file.exists():
        options = []
        for option_string, option in arg_parser._option_string_actions.items():
            if re.match('^-[a-gi-z]$', option_string):
                option_value = getattr(args, option.dest)
                if option_value != option.default:
                    if option.const in (True, False):
                        options.append(option_string[1])
                    else:
                        options.append(' {} {}'.format(option_string, option_value))
            elif args.operation is option.const:
                op_flag = option_string
        log_args = op_flag + ''.join(sorted(options, key=(lambda x: (len(x) != 1, x.upper())))).replace(' -', '', 1)
        terms = ' '.join('"{}"'.format(term.replace('"', '\\"')) for term in sorted(args.terms))
        with log_file.open('a') as fd:
            fd.write('{}\t{} -- {}'.format(datetime.today().isoformat(' '), log_args, terms).strip() + '\n')


def main():
    arg_parser = make_arg_parser()
    args = parse_args(arg_parser)
    journal = Journal(args.directory, use_cache=args.use_cache, ignores=args.ignores)
    if args.log:
        log_search(arg_parser, args, journal)
    args.operation(journal, args)


if __name__ == '__main__':
    main()
