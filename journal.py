#!/usr/bin/env python3

import re
import tarfile
from ast import literal_eval
from argparse import ArgumentParser
from collections import namedtuple, defaultdict
from copy import copy
from datetime import datetime, timedelta
from itertools import chain, groupby
from os import chdir as cd, chmod, environ, execvp, fork, remove as rm, wait, walk
from os.path import basename, exists as file_exists, expanduser, join as join_path, realpath, relpath
from stat import S_IRUSR
from statistics import mean, median, stdev
from sys import stdout, argv
from tempfile import mkstemp

Entry = namedtuple('Entry', 'date, text, filepath')

FILE_EXTENSION = '.journal'
STRING_LENGTHS = {
    'year': 4,
    'month': 7,
    'day': 10,
}
DATE_LENGTH = STRING_LENGTHS['day']
DATE_REGEX = re.compile('([0-9]{4}-[0-9]{2}-[0-9]{2})(, (Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day)?')
RANGE_REGEX = re.compile('^([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?:?([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?$')
REF_REGEX = re.compile('([0-9]{4}-[0-9]{2}-[0-9]{2})')


class Journal:

    DATE_REGEX = re.compile(
        '([0-9]{4}-[0-9]{2}-[0-9]{2})'
        '(, (Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day)?'
    )

    def __init__(self, directory, use_cache=True, ignores=None):
        self.directory = realpath(expanduser(directory))
        if ignores is None:
            ignores = []
        self.ignores = set(realpath(expanduser(filepath)) for filepath in ignores)
        self.use_cache = use_cache
        self.entries = {}
        self.metadata = {}
        self.tags = {}
        if self.use_cache:
            self._check_cache_files()
        self._initialize()

    def __getitem__(self, key):
        return self.entries[key]

    @property
    def journal_files(self):
        for path, _, files in walk(self.directory):
            for journal_file in files:
                if not journal_file.endswith(FILE_EXTENSION):
                    continue
                journal_file = join_path(path, journal_file)
                if journal_file in self.ignores:
                    continue
                yield journal_file

    @property
    def metadata_file(self):
        return join_path(self.directory, '.metadata')

    @property
    def tags_file(self):
        return join_path(self.directory, '.tags')

    @property
    def cache_file(self):
        return join_path(self.directory, '.cache')

    def _check_cache_files(self):
        cache_files = (
            self.metadata_file,
            self.tags_file,
            self.cache_file,
        )
        for cache_file in cache_files:
            if not file_exists(cache_file):
                raise OSError(f'cache file {cache_file} not found')

    def _initialize(self):
        self._read_files()
        self._load_metadata()

    def _read_file(self, filepath):
        with open(filepath) as fd:
            for raw_entry in fd.read().strip().split('\n\n'):
                if self.DATE_REGEX.match(raw_entry):
                    entry = Entry(
                        raw_entry[:DATE_LENGTH],
                        raw_entry,
                        filepath,
                    )
                    self.entries[entry.date] = entry

    def _read_files(self):
        if self.use_cache:
            self._read_file(self.cache_file)
        else:
            for path, _, files in walk(self.directory):
                for file in files:
                    if not file.endswith(FILE_EXTENSION):
                        continue
                    filepath = join_path(path, file)
                    if filepath in self.ignores:
                        continue
                    self._read_file(filepath)

    def _load_metadata(self):
        if not self.use_cache:
            return
        with open(self.metadata_file) as fd:
            self.metadata = literal_eval('{' + fd.read() + '}')
        with open(self.tags_file) as fd:
            for line in fd.read().splitlines():
                entry, filepath, line_number = line.split()
                self.tags[entry] = (filepath, line_number)

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
        for journal_file in self.journal_files:
            rel_path = relpath(journal_file, self.directory)
            with open(journal_file) as fd:
                lines = fd.read().splitlines()
            for line_number, line in enumerate(lines, start=1):
                if DATE_REGEX.match(line):
                    self.tags[line[:DATE_LENGTH]] = (rel_path, line_number)
        with open(self.metadata_file, 'w') as fd:
            fd.write(f'"updated":"{datetime.today().date().isoformat()}",\n')
        with open(self.tags_file, 'w') as fd:
            for tag, (filepath, line) in sorted(self.tags.items()):
                fd.write('\t'.join([tag, filepath, str(line)]) + '\n')
        with open(self.cache_file, 'w') as fd:
            for entry in sorted(self.entries.values()):
                fd.write(str(entry.text) + '\n\n')

    def verify(self):
        errors = []
        dates = set()
        long_dates = None
        for journal_file in self.journal_files:
            with open(journal_file) as fd:
                lines = fd.read().splitlines()
            prev_indent = 0
            for line_number, line in enumerate(lines, start=1):
                indent = len(re.match('\t*', line).group(0))
                if not re.fullmatch('(\t*([^ \t][ -~]*)?[^ \t])?', line):
                    errors.append((journal_file, line_number, 'non-tab indentation, ending blank, or non-ASCII character'))
                if not line.lstrip().startswith('|') and '  ' in line:
                    errors.append((journal_file, line_number, 'multiple spaces'))
                if indent == 0:
                    if DATE_REGEX.match(line):
                        entry_date = line[:DATE_LENGTH]
                        cur_date = datetime.strptime(entry_date, '%Y-%m-%d')
                        if prev_indent != 0:
                            errors.append((journal_file, line_number, 'no empty line between entries'))
                        if not entry_date.startswith(re.sub(FILE_EXTENSION, '', basename(journal_file))):
                            errors.append((journal_file, line_number, "filename doesn't match entry"))
                        if long_dates is None:
                            long_dates = (len(line) > DATE_LENGTH)
                        elif long_dates != (len(line) > DATE_LENGTH):
                            errors.append((journal_file, line_number, 'inconsistent date format'))
                        if long_dates and line != cur_date.strftime('%Y-%m-%d, %A'):
                            errors.append((journal_file, line_number, 'date-weekday correctness'))
                        if cur_date in dates:
                            errors.append((journal_file, line_number, 'duplicate dates'))
                        dates.add(cur_date)
                    else:
                        if line:
                            if line[0] == '\ufeff':
                                errors.append((journal_file, line_number, 'byte order mark'))
                            else:
                                errors.append((journal_file, line_number, 'unindented text'))
                        if prev_indent == 0:
                            errors.append((journal_file, line_number, 'consecutive unindented lines'))
                elif indent - prev_indent > 1:
                    errors.append((journal_file, line_number, 'unexpected indentation'))
                prev_indent = indent
            if prev_indent == 0:
                errors.append((journal_file, len(lines), 'file ends on blank line'))
        if errors:
            print('\n'.join('{}:{}: {}'.format(*error) for error in sorted(errors)))
            exit(1)


# utility functions


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


def get_journal_files(args):
    journal_files = set()
    for path, _, files in walk(args.directory):
        journal_files.update(join_path(path, f) for f in files if f.endswith(FILE_EXTENSION))
    journal_files -= args.ignores
    return journal_files


# operations


def do_archive(directory):
    filename = 'jrnl' + datetime.now().strftime('%Y%m%d%H%M%S')
    with tarfile.open('{}.txz'.format(filename), 'w:xz') as tar:
        tar.add(directory, arcname=filename, filter=(lambda tarinfo: None if basename(tarinfo.name)[0] in '._' else tarinfo))
        tar.add(argv[0], arcname=join_path(filename, basename(argv[0])))


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

    entries = journal.filter(
        terms=args.terms,
        date_ranges=args.date_ranges,
        icase=args.icase,
    )
    columns = ['DATE', 'POSTS', 'FREQ', 'SIZE', 'WORDS', 'MIN', 'MED', 'MAX', 'MEAN', 'STDEV']
    unit_length = STRING_LENGTHS[args.unit]
    length_map = {
        date: len(entry.text.split())
        for date, entry in entries.items()
    }
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


def do_graph(journal, args):
    entries = journal.filter(
        terms=args.terms,
        date_ranges=args.date_ranges,
        icase=args.icase,
    )
    disjoint_sets = dict((k, k) for k in entries)
    ancestors = defaultdict(set)
    edges = dict((k, set()) for k in entries)
    for src in sorted(entries):
        dests = set(dest for dest in REF_REGEX.findall(entries[src]) if src > dest and dest in entries)
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
                print('\n'.join('\t"{}" -> "{}";'.format(src, dest) for dest in sorted(edges[src], reverse=args.reverse)))
        print('')
    print('}')


def do_list(journal, args):
    entries = journal.filter(
        terms=args.terms,
        date_ranges=args.date_ranges,
        icase=args.icase,
    )
    print('\n'.join(sorted(entries.keys())))


def do_show(journal, args):
    entries = journal.filter(
        terms=args.terms,
        date_ranges=args.date_ranges,
        icase=args.icase,
    )
    text = '\n\n'.join(entry.text for _, entry in sorted(entries.items()))
    if stdout.isatty():
        temp_file = mkstemp(FILE_EXTENSION)[1]
        with open(temp_file, 'w') as fd:
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


def do_update(journal, _):
    journal.update_metadata()


def do_verify(journal, _):
    journal.verify()


# CLI


def make_arg_parser():
    # pylint: disable = line-too-long
    arg_parser = ArgumentParser(usage='%(prog)s <operation> [options] [TERM ...]', description='A command line tool for viewing and maintaining a journal.')
    arg_parser.set_defaults(directory='./', ignores=[], icase=re.IGNORECASE, terms=[], unit='year')
    arg_parser.add_argument('terms', metavar='TERM', nargs='*', help='pattern which must exist in entries')
    group = arg_parser.add_argument_group('OPERATIONS').add_mutually_exclusive_group(required=True)
    group.add_argument('-A', dest='operation', action='store_const', const='archive', help='archive to datetimed tarball')
    group.add_argument('-C', dest='operation', action='store_const', const='count', help='count words and entries')
    group.add_argument('-G', dest='operation', action='store_const', const='graph', help='graph entry references in DOT')
    group.add_argument('-L', dest='operation', action='store_const', const='list', help='list entry dates')
    group.add_argument('-S', dest='operation', action='store_const', const='show', help='show entry contents')
    group.add_argument('-U', dest='operation', action='store_const', const='update', help='update tags and cache file')
    group.add_argument('-V', dest='operation', action='store_const', const='verify', help='verify journal sanity')
    group = arg_parser.add_argument_group('INPUT OPTIONS')
    group.add_argument('--directory', dest='directory', action='store', help='use journal files in directory')
    group.add_argument('--ignore', dest='ignores', action='append', help='ignore specified file')
    group.add_argument('--skip-cache', dest='skip_cache', action='store_true', help='skip cached entries and indices')
    group = arg_parser.add_argument_group('FILTER OPTIONS (APPLIES TO -[CGLS])')
    group.add_argument('-d', dest='date_ranges', action='store', help='only use entries in range')
    group.add_argument('-i', dest='icase', action='store_false', help='ignore case-insensitivity')
    group.add_argument('-n', dest='num_results', action='store', type=int, help='limit number of results')
    group = arg_parser.add_argument_group('OUTPUT OPTIONS')
    group.add_argument('-r', dest='reverse', action='store_true', help='reverse chronological order')
    group = arg_parser.add_argument_group('OPERATION-SPECIFIC OPTIONS')
    group.add_argument('--no-headers', dest='headers', action='store_false', help='[C] do not print headers')
    group.add_argument('--unit', dest='unit', action='store', choices=('year', 'month', 'day'), help='[C] set tabulation unit')
    return arg_parser


def parse_args():
    arg_parser = make_arg_parser()
    args = arg_parser.parse_args()
    if args.date_ranges:
        date_ranges = []
        for date_range in args.date_ranges.split(','):
            if not (date_range and RANGE_REGEX.match(date_range)):
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
    args.directory = realpath(expanduser(args.directory))
    args.ignores = set(realpath(expanduser(path.strip())) for arg in args.ignores for path in arg.split(','))
    args.terms = set(args.terms)
    return args


def main():
    args = parse_args()
    journal = Journal(args.directory, ignores=args.ignores)
    globals()[f'do_{args.operation}'](journal, args)


if __name__ == '__main__':
    main()
