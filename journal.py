#!/usr/bin/env python3.4

import re
import tarfile
from ast import literal_eval
from argparse import ArgumentParser
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta
from itertools import chain, groupby
from os import chdir as cd, chmod, execvp, fork, remove as rm, wait, walk
from os.path import basename, exists as file_exists, expanduser, getmtime, join as join_path, realpath, relpath
from stat import S_IRUSR
from statistics import mean, median, stdev
from sys import stdin, stdout, argv
from tempfile import mkstemp

FILE_EXTENSION = ".journal"
DATE_REGEX = re.compile("([0-9]{4}-[0-9]{2}-[0-9]{2})(, (Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day)?")
RANGE_REGEX = re.compile("^([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?:?([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?$")
REF_REGEX = re.compile("([0-9]{4}-[0-9]{2}-[0-9]{2})")
YEAR_LENGTH = 4
MONTH_LENGTH = 7
DATE_LENGTH = 10

arg_parser = ArgumentParser(usage="%(prog)s <operation> [options] [TERM ...]", description="a command line tool for viewing and maintaining a journal")
arg_parser.set_defaults(directory="./", ignores=[], icase=re.IGNORECASE, num_results=0, reverse=False, log=True, unit="year", use_cache="yes", use_index="yes")
arg_parser.add_argument("terms", metavar="TERM", nargs="*", help="pattern which must exist in entries")
group = arg_parser.add_argument_group("OPERATIONS").add_mutually_exclusive_group(required=True)
group.add_argument("-A",          dest="action",      action="store_const", const="archive",                   help="archive to datetimed tarball")
group.add_argument("-C",          dest="action",      action="store_const", const="count",                     help="count words and entries")
group.add_argument("-G",          dest="action",      action="store_const", const="graph",                     help="graph entry references in DOT")
group.add_argument("-L",          dest="action",      action="store_const", const="list",                      help="list entry dates")
group.add_argument("-S",          dest="action",      action="store_const", const="show",                      help="show entry contents")
group.add_argument("-U",          dest="action",      action="store_const", const="update",                    help="update tags and cache file")
group.add_argument("-V",          dest="action",      action="store_const", const="verify",                    help="verify journal sanity")
group = arg_parser.add_argument_group("INPUT OPTIONS")
group.add_argument("--directory", dest="directory",   action="store",                                          help="use journal files in directory")
group.add_argument("--ignore",    dest="ignores",     action="append",                                         help="ignore specified file")
group.add_argument("--use-cache", dest="use_cache",   action="store",       choices=("yes", "no"),             help="use cached entries")
group.add_argument("--use-index", dest="use_index",   action="store",       choices=("yes", "no"),             help="use cached indices")
group = arg_parser.add_argument_group("FILTER OPTIONS (APPLIES TO -[CGLS])")
group.add_argument("-d",          dest="date_range",  action="store",                                          help="only use entries in range")
group.add_argument("-i",          dest="icase",       action="store_false",                                    help="ignore case-insensitivity")
group.add_argument("-n",          dest="num_results", action="store",       type=int,                          help="max number of results")
group = arg_parser.add_argument_group("OUTPUT OPTIONS")
group.add_argument("-r",          dest="reverse",     action="store_true",                                     help="reverse chronological order")
group = arg_parser.add_argument_group("OPERATION-SPECIFIC OPTIONS")
group.add_argument("--no-log",    dest="log",         action="store_false",                                    help="[S] do not log search")
group.add_argument("--unit",      dest="unit",        action="store",       choices=("year", "month", "date"), help="[C] tabulation unit")
args = arg_parser.parse_args()

is_maintenance_op = (args.action in ("archive", "update", "archive"))

if args.date_range and not all(dr and RANGE_REGEX.match(dr) for dr in args.date_range.split(",")):
    arg_parser.error("argument -d: '{}' should be in format [YYYY[-MM[-DD]]][:][YYYY[-MM[-DD]]][,...]".format(args.date_range))
if not stdin.isatty() and is_maintenance_op:
    arg_parser.error("argument -[ATV]: operation can only be performed on files")
args.directory = realpath(expanduser(args.directory))
args.ignores = set(realpath(expanduser(path)) for path in args.ignores)
args.terms = set(args.terms)
if is_maintenance_op:
    args.date_range = None
    args.icase = re.IGNORECASE
    args.reverse = False
    args.use_cache = "no"
    args.use_index = "yes"
args.use_cache = (args.use_cache == "yes")
args.use_index = (args.use_index == "yes")

if args.action == "archive":
    filename = "jrnl" + datetime.now().strftime("%Y%m%d%H%M%S")
    with tarfile.open("{}.txz".format(filename), "w:xz") as tar:
        tar.add(args.directory, arcname=filename, filter=(lambda tarinfo: None if basename(tarinfo.name).startswith(".") else tarinfo))
        tar.add(argv[0], arcname=join_path(filename, basename(argv[0])))
    exit()

log_file = join_path(args.directory, ".log") if stdin.isatty() else ""
tags_file = join_path(args.directory, "tags") if stdin.isatty() else ""
cache_file = join_path(args.directory, ".cache") if stdin.isatty() else ""
index_file = join_path(args.directory, ".index") if stdin.isatty() else ""

journal_files = set()
raw_entries = ""
entries = {}
if not stdin.isatty():
    raw_entries = stdin.read()
elif file_exists(cache_file) and args.use_cache:
    with open(cache_file) as fd:
        raw_entries = fd.read()
else:
    for path, dirs, files in walk(args.directory):
        journal_files.update(join_path(path, f) for f in files if f.endswith(FILE_EXTENSION))
    journal_files -= args.ignores
    file_entries = []
    for journal in journal_files:
        with open(journal) as fd:
            file_entries.append(fd.read().strip())
    raw_entries = "\n\n".join(file_entries)
if not raw_entries:
    arg_parser.error("no journal entries found or specified")
entries.update((entry[:DATE_LENGTH], entry.strip()) for entry in raw_entries.strip().split("\n\n") if entry and DATE_REGEX.match(entry))

index = defaultdict(set)
index_metadata = {}
if file_exists(index_file):
    with open(index_file) as fd:
        index_metadata = literal_eval("{" + fd.readline()[2:] + "}")
        index = literal_eval("{" + "".join(line for line in fd.read().splitlines() if not line.startswith("#")) + "}")
        for term in index:
            index[term] = set(index[term])

entry_file_map = {}
if file_exists(tags_file):
    with open(tags_file) as fd:
        entry_file_map = dict(line.split()[0:2] for line in fd.read().splitlines())

selected = set(entries.keys())
unindexed_terms = set()
if args.action == "update":
    unindexed_terms = set(index.keys())
    if args.use_index:
        update_timestamp = datetime.strptime(index_metadata["updated"], "%Y-%m-%d").timestamp()
        selected = set(k for k, v in entry_file_map.items() if getmtime(v) > update_timestamp)
        for term in index:
            index[term] -= selected
else:
    selected.intersection_update(*(index[term.lower()] for term in args.terms if term.lower() in index))
    unindexed_terms = set(term for term in args.terms if term not in index)

if args.date_range:
    first_date = min(selected)
    last_date = (datetime.strptime(max(selected), "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    selected = set()
    for date_range in args.date_range.split(","):
        if ":" in date_range:
            start_date, end_date = date_range.split(":")
            start_date, end_date = (start_date or first_date, end_date or last_date)
            start_date += "-01" * int((DATE_LENGTH - len(start_date)) / 3)
            end_date += "-01" * int((DATE_LENGTH - len(end_date)) / 3)
            selected |= set(k for k in entries if start_date <= k < end_date)
        else:
            selected |= set(k for k in entries if k.startswith(date_range))

# FIXME this code is UGLY
index_updates = defaultdict(set)
if args.action == "update" and selected:
    for term in unindexed_terms:
        term = term.lower()
        index_updates[term] = set(k for k in selected if re.search(term, entries[k], flags=(re.IGNORECASE | re.MULTILINE)))
elif len(entries) == len(selected):
    for term in unindexed_terms:
        term = term.lower()
        index_updates[term] = set(k for k in entries.keys() if re.search(term, entries[k], flags=(re.IGNORECASE | re.MULTILINE)))
        selected &= index_updates[term]

if args.action == "update":
    tags = []
    for journal in journal_files:
        rel_path = relpath(journal, args.directory)
        with open(journal) as fd:
            lines = fd.read().splitlines()
        for line_number, line in enumerate(lines, start=1):
            if DATE_REGEX.match(line):
                tags.append((line[:DATE_LENGTH], rel_path, line_number))
    with open(tags_file, "w") as fd:
        fd.write("\n".join("{}\t{}\t{}".format(*tag) for tag in sorted(tags)))
    with open(cache_file, "w") as fd:
        fd.write("\n\n".join(sorted(entries.values())))
    with open(index_file, "w") as fd:
        fd.write('# "updated":"{}"\n'.format(datetime.now().strftime("%Y-%m-%d")))
        for term in sorted(set(index.keys()) | set(index_updates.keys())):
            fd.write("\"{}\": {},\n".format(term.replace('"', '\\"'), sorted(index[term] | index_updates[term])))
    exit()

if not is_maintenance_op and index_updates:
    with open(index_file, "a") as fd:
        fd.write("".join("\"{}\": {},\n".format(k.lower().replace('"', '\\"'), sorted(v)) for k, v in index_updates.items()))

if not is_maintenance_op:
    for term in unindexed_terms:
        selected = set(k for k in selected if re.search(term, entries[k], flags=(args.icase | re.MULTILINE)))

if not selected:
    exit()

if not is_maintenance_op:
    selected = sorted(selected, reverse=args.reverse)
    if args.num_results > 0:
        selected = selected[:args.num_results]

if args.action == "count":
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
    header = tuple(columns.keys())
    widths = tuple(max(len(row[col]) for row in chain((header,), table)) for col in range(len(columns)))
    print(gap.join(col.center(widths[i]) for i, col in enumerate(header)))
    print(gap.join(width * "-" for width in widths))
    print("\n".join(gap.join(col.rjust(widths[i]) for i, col in enumerate(row)) for row in table))

elif args.action == "graph":
    disjoint_sets = dict((k, k) for k in selected)
    ancestors = {}
    edges = dict((k, set()) for k in selected)
    for src in sorted(selected):
        dests = set(dest for dest in REF_REGEX.findall(entries[src]) if src > dest and dest in selected)
        ancestors[src] = set().union(*(ancestors.get(parent, set()) for parent in dests))
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
                print("\n".join('\t"{}" -> "{}"'.format(src, dest) for dest in sorted(edges[src], reverse=args.reverse)))
        print("")
    print('}')

elif args.action == "list":
    print("\n".join(selected))

elif args.action == "show":
    if file_exists(log_file) and args.log:
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
            fd.write("{}\t{} {}\n".format(datetime.today().isoformat(" "), options, terms))
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
                vim_args[-1] += " " + ("noignorecase" if args.icase else "nosmartcase")
                vim_args.extend(("-c", "let @/=\"\\\\v" + "|".join("({})".format(term) for term in args.terms).replace('"', r'\"').replace("@", r"\\@") + "\""))
            execvp("nvim", vim_args)
    else:
        print(text)

elif args.action == "verify":
    errors = []
    dates = set()
    long_dates = None
    for journal in journal_files:
        with open(journal) as fd:
            lines = fd.read().splitlines()
        prev_indent = 0
        for line_number, line in enumerate(lines, start=1):
            if not line:
                continue
            indent = len(re.match("\t*", line).group(0))
            if indent - prev_indent > 1:
                errors.append((journal, line_number, "unexpected indentation"))
            if not re.search("^\t*[^ \t][ -~]*[^ \t]$", line):
                errors.append((journal, line_number, "non-tab indentation, ending space, or non-ASCII character"))
            if not line.strip().startswith("|") and "  " in line:
                errors.append((journal, line_number, "multiple spaces"))
            if indent == 0:
                if DATE_REGEX.match(line):
                    entry_date = line[:DATE_LENGTH]
                    cur_date = datetime.strptime(entry_date, "%Y-%m-%d")
                    if not entry_date.startswith(re.sub(FILE_EXTENSION, "", basename(journal))):
                        errors.append((journal, line_number, "filename doesn't match entry"))
                    if long_dates is None:
                        long_dates = (len(line) > DATE_LENGTH)
                    elif long_dates != (len(line) > DATE_LENGTH):
                        errors.append((journal, line_number, "inconsistent date format"))
                    if long_dates and line != cur_date.strftime("%Y-%m-%d, %A"):
                        errors.append((journal, line_number, "date correctness"))
                    if cur_date in dates:
                        errors.append((journal, line_number, "duplicate dates"))
                    dates.add(cur_date)
                else:
                    errors.append((journal, line_number, "unindented text"))
            prev_indent = indent
    has_errors = False
    if errors:
        print("\n".join("{}:{}: {}".format(*error) for error in errors))
        has_errors = True
    errors = []
    for key, value in sorted(entries.items()):
        if value.count('"') % 2:
            errors.append((key, "odd quotation marks"))
    if errors:
        print("\n".join("{}: {}".format(*error) for error in errors))
        has_errors = True
    if has_errors:
        exit(1)
