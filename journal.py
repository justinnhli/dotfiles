#!/usr/bin/env python3.4

import re
import tarfile
from ast import literal_eval
from argparse import ArgumentParser
from collections import defaultdict, OrderedDict
from copy import copy
from datetime import datetime, timedelta
from itertools import chain, groupby
from os import chdir as cd, chmod, execvp, fork, remove as rm, wait, walk
from os.path import basename, exists as file_exists, expanduser, getmtime, join as join_path, realpath, relpath
from stat import S_IRUSR
from statistics import mean, median, stdev
from sys import stdout, argv
from tempfile import mkstemp

FILE_EXTENSION = ".journal"
DATE_REGEX = re.compile("([0-9]{4}-[0-9]{2}-[0-9]{2})(, (Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day)?")
RANGE_REGEX = re.compile("^([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?:?([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?$")
REF_REGEX = re.compile("([0-9]{4}-[0-9]{2}-[0-9]{2})")
YEAR_LENGTH = 4
MONTH_LENGTH = 7
DATE_LENGTH = 10

LOG_FILE = ".log"
METADATA_FILE = ".metadata"
TAGS_FILE = ".tags"
CACHE_FILE = ".cache"
INDEX_FILE = ".index"

arg_parser = ArgumentParser(usage="%(prog)s <operation> [options] [TERM ...]", description="A command line tool for viewing and maintaining a journal.")
arg_parser.set_defaults(directory="./", headers=True, ignores=[], icase=re.IGNORECASE, reverse=False, log=True, unit="year", use_cache="yes")
arg_parser.add_argument("terms", metavar="TERM", nargs="*", help="pattern which must exist in entries")
group = arg_parser.add_argument_group("OPERATIONS").add_mutually_exclusive_group(required=True)
group.add_argument("-A",           dest="op",          action="store_const", const="archive",                   help="archive to datetimed tarball")
group.add_argument("-C",           dest="op",          action="store_const", const="count",                     help="count words and entries")
group.add_argument("-G",           dest="op",          action="store_const", const="graph",                     help="graph entry references in DOT")
group.add_argument("-L",           dest="op",          action="store_const", const="list",                      help="list entry dates")
group.add_argument("-S",           dest="op",          action="store_const", const="show",                      help="show entry contents")
group.add_argument("-U",           dest="op",          action="store_const", const="update",                    help="update tags and cache file")
group.add_argument("-V",           dest="op",          action="store_const", const="verify",                    help="verify journal sanity")
group = arg_parser.add_argument_group("INPUT OPTIONS")
group.add_argument("--directory",  dest="directory",   action="store",                                          help="use journal files in directory")
group.add_argument("--ignore",     dest="ignores",     action="append",                                         help="ignore specified file")
group.add_argument("--use-cache",  dest="use_cache",   action="store",       choices=("yes", "no"),             help="use cached entries and indices")
group = arg_parser.add_argument_group("FILTER OPTIONS (APPLIES TO -[CGLS])")
group.add_argument("-d",           dest="date_range",  action="store",                                          help="only use entries in range")
group.add_argument("-i",           dest="icase",       action="store_false",                                    help="ignore case-insensitivity")
group.add_argument("-n",           dest="num_results", action="store",       type=int,                          help="limit number of results")
group = arg_parser.add_argument_group("OUTPUT OPTIONS")
group.add_argument("-r",           dest="reverse",     action="store_true",                                     help="reverse chronological order")
group = arg_parser.add_argument_group("OPERATION-SPECIFIC OPTIONS")
group.add_argument("--no-log",     dest="log",         action="store_false",                                    help="[S] do not log search")
group.add_argument("--no-headers", dest="headers",     action="store_false",                                    help="[C] do not print headers")
group.add_argument("--unit",       dest="unit",        action="store",       choices=("year", "month", "date"), help="[C] set tabulation unit")
args = arg_parser.parse_args()

is_maintenance_op = args.op in ("archive", "update", "verify")
if is_maintenance_op:
    for option_dest in ("date_range", "icase", "terms"):
        for option_string, option in arg_parser._option_string_actions.items():
            if option_dest == option.dest:
                setattr(args, option_dest, option.default)

if args.date_range and not all(dr and RANGE_REGEX.match(dr) for dr in args.date_range.split(",")):
    arg_parser.error("argument -d: '{}' should be in format [YYYY[-MM[-DD]]][:][YYYY[-MM[-DD]]][,...]".format(args.date_range))
if args.num_results is not None and args.num_results < 1:
    arg_parser.error("argument -n: '{}' should be a positive integer".format(args.num_results))
args.directory = realpath(expanduser(args.directory))
args.ignores = set(realpath(expanduser(path.strip())) for arg in args.ignores for path in arg.split(","))
args.terms = set(args.terms)

if args.op == "archive":
    filename = "jrnl" + datetime.now().strftime("%Y%m%d%H%M%S")
    with tarfile.open("{}.txz".format(filename), "w:xz") as tar:
        tar.add(args.directory, arcname=filename, filter=(lambda tarinfo: None if basename(tarinfo.name).startswith(".") else tarinfo))
        tar.add(argv[0], arcname=join_path(filename, basename(argv[0])))
    exit()

log_file = join_path(args.directory, LOG_FILE)
metadata_file = join_path(args.directory, METADATA_FILE)
tags_file = join_path(args.directory, TAGS_FILE)
cache_file = join_path(args.directory, CACHE_FILE)
index_file = join_path(args.directory, INDEX_FILE)

use_index = True
if args.use_cache == "yes":
    if all(file_exists(file) for file in (metadata_file, tags_file, cache_file, index_file)):
        use_index = True
    elif args.op == "update":
        use_index = False
    else:
        arg_parser.error("argument -[CGLSV]: cache files corrupted or not found; please run -U first")

journal_files = set()
entries = ""
if not is_maintenance_op and use_index:
    with open(cache_file) as fd:
        entries = fd.read()
else:
    for path, dirs, files in walk(args.directory):
        journal_files.update(join_path(path, f) for f in files if f.endswith(FILE_EXTENSION))
    journal_files -= args.ignores
    file_entries = []
    for journal in journal_files:
        with open(journal) as fd:
            file_entries.append(fd.read().strip())
    entries = "\n\n".join(file_entries)
if not entries:
    arg_parser.error("no journal entries found or specified")
entries = dict((entry[:DATE_LENGTH], entry.strip()) for entry in entries.strip().split("\n\n") if entry and DATE_REGEX.match(entry))

if args.op == "show" and args.log and file_exists(log_file):
    options = []
    for option_string, option in arg_parser._option_string_actions.items():
        if re.match("^-[a-gi-z]$", option_string):
            option_value = getattr(args, option.dest)
            if option_value != option.default:
                if option.const in (True, False):
                    options.append(option_string[1])
                else:
                    options.append(" {} {}".format(option_string, option_value))
    options = "-S" + "".join(sorted(options, key=(lambda x: (len(x) != 1, x.upper())))).replace(" -", "", 1)
    terms = " ".join('"{}"'.format(term.replace('"', '\\"')) for term in sorted(args.terms))
    with open(log_file, "a") as fd:
        fd.write("{}\t{} -- {}".format(datetime.today().isoformat(" "), options, terms).strip() + "\n")

metadata = {}
index = defaultdict(set)
tags = {}
if use_index:
    with open(metadata_file) as fd:
        metadata = literal_eval("{" + fd.read() + "}")
    with open(index_file) as fd:
        index = literal_eval("{" + fd.read() + "}")
        for term in index:
            index[term] = set(index[term])
    with open(tags_file) as fd:
        for line in fd.read().splitlines():
            entry, file, line_number = line.split()
            tags[entry] = (file, line_number)

selected = set(entries.keys())

if is_maintenance_op and use_index:
    update_timestamp = datetime.strptime(metadata["updated"], "%Y-%m-%d").timestamp()
    for entry, file_line in tags.items():
        file = file_line[0]
        if getmtime(file) < update_timestamp:
            journal_files.discard(join_path(args.directory, file))
            selected.remove(entry)
    for term in index:
        index[term] -= selected

unindexed_terms = args.terms
if args.op == "update":
    unindexed_terms = set(index.keys())
elif use_index:
    selected.intersection_update(*(index[term.lower()] for term in args.terms if term.lower() in index))
    unindexed_terms = set(term for term in args.terms if term not in index)

candidates = copy(selected)
if args.date_range:
    first_date = min(selected)
    last_date = (datetime.strptime(max(selected), "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    selected = set()
    for date_range in args.date_range.split(","):
        if ":" in date_range:
            start_date, end_date = date_range.split(":")
            start_date, end_date = (start_date or first_date, end_date or last_date)
            start_date, end_date = (date + "-01" * int((DATE_LENGTH - len(date)) / len("-01")) for date in (start_date, end_date))
            selected |= set(k for k in candidates if start_date <= k < end_date)
        else:
            selected |= set(k for k in candidates if k.startswith(date_range))

candidates = copy(selected)
index_updates = defaultdict(set)
if args.op == "update" or len(entries) == len(candidates):
    for term in unindexed_terms:
        term = term.lower()
        index_updates[term] = set(k for k in candidates if re.search(term, entries[k], flags=(re.IGNORECASE | re.MULTILINE)))
        selected &= index_updates[term]

if not is_maintenance_op:
    if index_updates:
        with open(index_file, "a") as fd:
            fd.write("".join("\"{}\": {},\n".format(k.lower().replace('"', '\\"'), sorted(v)) for k, v in index_updates.items()))

    if not is_maintenance_op:
        for term in unindexed_terms:
            selected = set(k for k in selected if re.search(term, entries[k], flags=(args.icase | re.MULTILINE)))

    selected = sorted(selected, reverse=args.reverse)
    if args.num_results:
        selected = selected[:args.num_results]

    if not selected:
        exit()

if args.op == "count":
    gap_size = 2
    gap = gap_size * " "
    columns = OrderedDict((
        ("DATE",  (lambda u, p, ds, ls: u)),
        ("POSTS", (lambda u, p, ds, ls: p)),
        ("FREQ",  (lambda u, p, ds, ls: format(((datetime.strptime(max(ds), "%Y-%m-%d") - datetime.strptime(min(ds), "%Y-%m-%d")).days + 1) / p, ".2f"))),
        ("SIZE",  (lambda u, p, ds, ls: format(sum(len(entries[k]) for k in ds), ",d"))),
        ("WORDS", (lambda u, p, ds, ls: format(sum(ls), ",d"))),
        ("MIN",   (lambda u, p, ds, ls: min(ls))),
        ("MED",   (lambda u, p, ds, ls: round(median(ls)))),
        ("MAX",   (lambda u, p, ds, ls: max(ls))),
        ("MEAN",  (lambda u, p, ds, ls: round(mean(ls)))),
        ("STDEV", (lambda u, p, ds, ls: round(stdev(ls)) if len(ls) > 1 else 0)),
    ))
    unit_length = locals()[args.unit.upper() + "_LENGTH"]
    length_map = dict((date, len(entries[date].split())) for date in selected)
    table = []
    for unit, dates in chain(groupby(selected, (lambda k: k[:unit_length])), (("all", selected),)):
        dates = tuple(dates)
        posts = len(dates)
        lengths = tuple(length_map[date] for date in dates)
        table.append(tuple(str(fn(unit, posts, dates, lengths)) for fn in columns.values()))
    headers = tuple(columns.keys())
    widths = tuple(max(len(row[col]) for row in chain((headers,), table)) for col in range(len(columns)))
    if args.headers:
        print(gap.join(col.center(widths[i]) for i, col in enumerate(headers)))
        print(gap.join(width * "-" for width in widths))
    print("\n".join(gap.join(col.rjust(widths[i]) for i, col in enumerate(row)) for row in table))

elif args.op == "graph":
    disjoint_sets = dict((k, k) for k in selected)
    ancestors = defaultdict(set)
    edges = dict((k, set()) for k in selected)
    for src in sorted(selected):
        dests = set(dest for dest in REF_REGEX.findall(entries[src]) if src > dest and dest in selected)
        ancestors[src] = set().union(*(ancestors[parent] for parent in dests))
        for dest in dests - ancestors[src]:
            edges[src].add(dest)
            while disjoint_sets[dest] != src:
                disjoint_sets[dest], dest = src, disjoint_sets[dest]
        ancestors[src] |= dests
    components = defaultdict(set)
    for rep in disjoint_sets:
        path = set((rep,))
        while disjoint_sets[rep] != rep:
            path.add(rep)
            rep = disjoint_sets[rep]
        components[rep] |= path
    print('digraph {')
    print('\tgraph [size="48", model="subset", rankdir="{}"];'.format('TB' if args.reverse else 'BT'))
    print('\tnode [fontcolor="#4E9A06", shape="none"];')
    print('\tedge [color="#555753"];')
    print("")
    for srcs in sorted(components.values(), key=(lambda s: (len(s), min(s))), reverse=(not args.reverse)):
        print('\t// component size = {}'.format(len(srcs)))
        for src in sorted(srcs, reverse=args.reverse):
            print('\t"{}" [fontsize="{}"];'.format(src, len(entries[src].split()) / 100))
            if edges[src]:
                print("\n".join('\t"{}" -> "{}";'.format(src, dest) for dest in sorted(edges[src], reverse=args.reverse)))
        print("")
    print('}')

elif args.op == "list":
    print("\n".join(selected))

elif args.op == "show":
    text = "\n\n".join(entries[k] for k in selected)
    if stdout.isatty():
        temp_file = mkstemp(FILE_EXTENSION)[1]
        with open(temp_file, "w") as fd:
            fd.write(text)
        chmod(temp_file, S_IRUSR)
        if fork():
            wait()
            rm(temp_file)
        else:
            cd(args.directory)
            vim_args = ["nvim", temp_file, "-c", "set hlsearch nospell"]
            if args.terms:
                vim_args[-1] += " " + ("nosmartcase" if args.icase else "noignorecase")
                vim_args.extend(("-c", r'let @/="\\v' + "|".join("({})".format(term) for term in args.terms).replace('"', r'\"').replace("@", r"\\@") + "\""))
            execvp("nvim", vim_args)
    else:
        print(text)

elif args.op == "update":
    for journal in journal_files:
        rel_path = relpath(journal, args.directory)
        with open(journal) as fd:
            lines = fd.read().splitlines()
        for line_number, line in enumerate(lines, start=1):
            if DATE_REGEX.match(line):
                tags[line[:DATE_LENGTH]] = (rel_path, line_number)
    with open(metadata_file, "w") as fd:
        fd.write('"updated":"{}",'.format(datetime.now().strftime("%Y-%m-%d")) + "\n")
    with open(tags_file, "w") as fd:
        fd.write("\n".join("{}\t{}\t{}".format(entry, *fileline) for entry, fileline in sorted(tags.items())) + "\n")
    with open(cache_file, "w") as fd:
        fd.write("\n\n".join(sorted(entries.values())) + "\n")
    with open(index_file, "w") as fd:
        for term in sorted(set(index.keys()) | set(index_updates.keys())):
            fd.write("\"{}\": {},\n".format(term.replace('"', '\\"'), sorted(index[term] | index_updates[term])))

elif args.op == "verify":
    errors = []
    dates = set()
    long_dates = None
    for journal in journal_files:
        with open(journal) as fd:
            lines = fd.read().splitlines()
        prev_indent = 0
        for line_number, line in enumerate(lines, start=1):
            indent = len(re.match("\t*", line).group(0))
            if not re.search("^(\t*([^ \t][ -~]*)?[^ \t])?$", line):
                errors.append((journal, line_number, "non-tab indentation, ending blank, or non-ASCII character"))
            if not line.strip().startswith("|") and "  " in line:
                errors.append((journal, line_number, "multiple spaces"))
            if indent == 0:
                if DATE_REGEX.match(line):
                    entry_date = line[:DATE_LENGTH]
                    cur_date = datetime.strptime(entry_date, "%Y-%m-%d")
                    if prev_indent != 0:
                        errors.append((journal, line_number, "no empty line between entries"))
                    if not entry_date.startswith(re.sub(FILE_EXTENSION, "", basename(journal))):
                        errors.append((journal, line_number, "filename doesn't match entry"))
                    if long_dates is None:
                        long_dates = (len(line) > DATE_LENGTH)
                    elif long_dates != (len(line) > DATE_LENGTH):
                        errors.append((journal, line_number, "inconsistent date format"))
                    if long_dates and line != cur_date.strftime("%Y-%m-%d, %A"):
                        errors.append((journal, line_number, "date-weekday correctness"))
                    if cur_date in dates:
                        errors.append((journal, line_number, "duplicate dates"))
                    dates.add(cur_date)
                else:
                    if line:
                        if line[0] == "\ufeff":
                            errors.append((journal, line_number, "byte order mark"))
                        else:
                            errors.append((journal, line_number, "unindented text"))
                    if prev_indent == 0:
                        errors.append((journal, line_number, "consecutive unindented lines"))
            elif indent - prev_indent > 1:
                errors.append((journal, line_number, "unexpected indentation"))
            prev_indent = indent
        if prev_indent == 0:
            errors.append((journal, len(lines), "file ends on blank line"))
    if errors:
        print("\n".join("{}:{}: {}".format(*error) for error in sorted(errors)))
        exit(1)
