#!/usr/bin/env python3

import re
import tarfile
from argparse import ArgumentParser
from datetime import datetime, timedelta
from itertools import chain, groupby
from math import floor
from os import chdir as cd, chmod, execvp, fork, remove as rm, wait, walk
from os.path import basename, exists as file_exists, expanduser, join as join_path, realpath, relpath
from stat import S_IRUSR
from sys import stdin, stdout, argv
from tempfile import mkstemp

DATE_REGEX = re.compile("([0-9]{4}-[0-9]{2}-[0-9]{2})(, (Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day)?")
RANGE_REGEX = re.compile("^([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?:?([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?$")
REF_REGEX = re.compile("([0-9]{4}-[0-9]{2}-[0-9]{2})")

arg_parser = ArgumentParser(usage="%(prog)s <operation> [options] [TERM ...]", description="a command line tool for viewing and maintaining a journal")
arg_parser.set_defaults(directory="./", ignores=[], case_sensitive=re.IGNORECASE, num_results=0, punctuation=True, reverse=False)
arg_parser.add_argument("terms",  metavar="TERM", nargs="*", help="pattern which must exist in entries")
group = arg_parser.add_argument_group("OPERATIONS").add_mutually_exclusive_group(required=True)
group.add_argument("-A",           dest="action",          action="store_const",  const="archive",  help="archive to datetimed tarball")
group.add_argument("-C",           dest="action",          action="store_const",  const="count",    help="count words and entries")
group.add_argument("-G",           dest="action",          action="store_const",  const="graph",    help="graph entry references in DOT")
group.add_argument("-L",           dest="action",          action="store_const",  const="list",     help="list entry dates")
group.add_argument("-S",           dest="action",          action="store_const",  const="show",     help="show entry contents")
group.add_argument("-U",           dest="action",          action="store_const",  const="update",   help="update tags and cache file")
group.add_argument("-V",           dest="action",          action="store_const",  const="verify",   help="verify journal sanity")
group = arg_parser.add_argument_group("INPUT OPTIONS")
group.add_argument("--directory",  dest="directory",       action="store",                          help="use journal files in directory")
group.add_argument("--ignore",     dest="ignores",         action="append",                         help="ignore specified file")
group = arg_parser.add_argument_group("FILTER OPTIONS (APPLIES TO -[CGLS])")
group.add_argument("-d",           dest="date_range",      action="store",                          help="only use entries in range")
group.add_argument("-i",           dest="case_sensitive",  action="store_false",                    help="ignore case-insensitivity")
group.add_argument("-n",           dest="num_results",     action="store",        type=int,         help="max number of results")
group = arg_parser.add_argument_group("OUTPUT OPTIONS")
group.add_argument("-r",           dest="reverse",         action="store_true",                     help="reverse chronological order")
args = arg_parser.parse_args()

if args.date_range and not all(dr and RANGE_REGEX.match(dr) for dr in args.date_range.split(",")):
	arg_parser.error("argument -d: '{}' should be in format [YYYY[-MM[-DD]]][:][YYYY[-MM[-DD]]][,...]".format(args.date_range))
if not stdin.isatty() and args.action in ("archive", "update", "verify"):
	arg_parser.error("argument -[ATV]: operation can only be performed on files")
args.directory = realpath(expanduser(args.directory))
args.ignores = set(realpath(expanduser(path)) for path in args.ignores)

log_file = join_path(args.directory, "log")
tags_file = join_path(args.directory, "tags")
cache_file = join_path(args.directory, ".cache")

if stdin.isatty():
	if args.action not in ("update", "verify") and file_exists(cache_file):
		with open(cache_file) as fd:
			raw_entries = fd.read()
	else:
		journal_files = set()
		for path, dirs, files in walk(args.directory):
			journal_files.update(join_path(path, f) for f in files if f.endswith(".journal"))
		journal_files = sorted(journal_files - args.ignores)
		raw_entries = "\n\n".join(open(journal, "r").read().strip() for journal in journal_files)
else:
	raw_entries = stdin.read()
if not raw_entries:
	arg_parser.error("no journal entries found or specified")
entries = dict((entry[:10], entry.strip()) for entry in raw_entries.strip().split("\n\n") if entry and DATE_REGEX.match(entry))

selected = set()
if args.date_range:
	first_date = min(entries.keys())
	last_date = (datetime.strptime(max(entries.keys()), "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
	for date_range in args.date_range.split(","):
		if ":" in date_range:
			start_date, end_date = date_range.split(":")
			start_date, end_date = (start_date or first_date, end_date or last_date)
			start_date += "-01" * int((10 - len(start_date)) / 2)
			end_date += "-01" * int((10 - len(end_date)) / 2)
			selected |= set(k for k in entries.keys() if (start_date <= k < end_date))
		else:
			selected |= set(k for k in entries.keys() if k.startswith(date_range))
else:
	selected = set(entries.keys())
if selected:
	for term in args.terms:
		selected = set(k for k in selected if re.search(term, entries[k], flags=args.case_sensitive|re.MULTILINE))
if selected:
	selected = sorted(selected, reverse=args.reverse)
	if args.num_results > 0:
		selected = selected[:args.num_results]

if args.action == "archive":
	filename = "jrnl{}".format(datetime.now().strftime("%Y%m%d%H%M%S"))
	with tarfile.open("{}.tbz".format(filename), "w:bz2") as tar:
		tar.add(args.directory, arcname=filename, filter=(lambda tarinfo: None if basename(tarinfo.name).startswith(".") else tarinfo))
		tar.add(argv[0], arcname=join_path(filename, basename(argv[0])))

elif args.action == "count" and selected:
	col_headers = ("YEAR", "POSTS", "WORDS", "MEAN", "MED", "MAX", "FREQ")
	table = []
	for year, dates in chain(groupby(selected, (lambda k: k[:4])), (("all", selected),)):
		dates = list(dates)
		posts = len(dates)
		lengths = sorted(len(entries[date].split()) for date in dates)
		words = sum(lengths)
		mean = round(words / posts)
		median = lengths[floor(posts / 2)]
		maximum = lengths[-1]
		freq = ((datetime.strptime(max(dates), "%Y-%m-%d") - datetime.strptime(min(dates), "%Y-%m-%d")).days + 1) / posts
		table.append((year, str(posts), format(words, ",d"), str(mean), str(median), str(maximum), "{:.3f}".format(freq)))
	widths = list(max(len(row[col]) for row in ([col_headers,] + table)) for col in range(0, len(col_headers)))
	print("  ".join(col.center(widths[i]) for i, col in enumerate(col_headers)))
	print("  ".join(width * "-" for width in widths))
	print("\n".join("  ".join(col.rjust(widths[i]) for i, col in enumerate(row)) for row in table))

elif args.action == "graph" and selected:
	print('digraph {')
	print('\tgraph [size="48", model="subset", rankdir="{}"];'.format('TB' if args.reverse else 'BT'))
	print('\tnode [fontcolor="#4E9A06", shape="none"];')
	print('\tedge [color="#555753"];')
	print()
	disjoint_sets = dict((k, k) for k in selected)
	ancestors = {}
	edges = dict((k, set()) for k in selected)
	for src in sorted(selected):
		dests = set(dest for dest in REF_REGEX.findall(entries[src]) if src > dest and dest in selected)
		ancestors[src] = set().union(*(ancestors.get(parent, set()) for parent in dests))
		for dest in (dests - ancestors[src]):
			edges[src].add('\t"{}" -> "{}";'.format(src, dest))
			path = set((src, dest))
			rep = dest
			for rep in (src, dest):
				while disjoint_sets[rep] != rep:
					path.add(rep)
					rep = disjoint_sets[rep]
				path.add(rep)
			for node in path:
				disjoint_sets[node] = rep
		ancestors[src] |= dests
	for rep in disjoint_sets:
		path = set()
		while disjoint_sets[rep] != rep:
			path.add(rep)
			rep = disjoint_sets[rep]
		path.add(rep)
		for node in path:
			disjoint_sets[node] = rep
	groups = dict((k, list(v)) for k, v in groupby(sorted(selected, key=(lambda k: disjoint_sets[k])), (lambda k: disjoint_sets[k])))
	for rep, srcs in sorted(groups.items(), reverse=(not args.reverse), key=(lambda x: len(x[1]))):
		print('\t// component size {}'.format(len(srcs)))
		for src in sorted(srcs, reverse=args.reverse):
			print('\t"{}" [fontsize="{}"];'.format(src, len(entries[src].split()) / 100))
			if edges[src]:
				print("\n".join(sorted(edges[src], reverse=args.reverse)))
		print()
	print('}')

elif args.action == "list" and selected:
	print("\n".join(selected))

elif args.action == "show" and selected:
	if file_exists(log_file):
		args_dict = vars(args)
		options = []
		for option_string, option in vars(arg_parser)["_option_string_actions"].items():
			if re.match("^-[a-gi-z]$", option_string):
				option = vars(option)
				option_value = args_dict[option["dest"]]
				if option_value != option["default"]:
					if option["const"] in (True, False):
						options.append(option_string[1])
					else:
						options.append(" {} {}".format(option_string, option_value))
		options = "-S" + "".join(sorted(options, key=(lambda x: (len(x) != 1, x.upper())))).replace(" -", "", 1)
		terms = " ".join('"{}"'.format(term) for term in sorted(args.terms))
		with open(log_file, "a") as fd:
			fd.write("{}\t{} {}\n".format(datetime.today().isoformat(" "), options, terms))
	text = "\n\n".join(entries[k] for k in selected)
	if stdout.isatty():
		temp_file = mkstemp(".journal")[1]
		with open(temp_file, "w") as fd:
			fd.write(text)
		chmod(temp_file, S_IRUSR)
		if fork():
			wait()
			rm(temp_file)
		else:
			cd(args.directory)
			vim_args = ["vim", temp_file, "-c", "set hlsearch nospell"]
			if args.terms:
				if args.case_sensitive:
					vim_args[-1] += " nosmartcase"
				else:
					vim_args[-1] += " noignorecase"
				vim_args.extend(["-c", "let @/=\"\\\\v" + "|".join("({})".format(term) for term in args.terms).replace('"', r'\"').replace("@", r"\\@") + "\""])
			execvp("vim", vim_args)
	else:
		print(text)

elif args.action == "update":
	tags = {}
	for journal in journal_files:
		with open(journal, "r") as fd:
			text = fd.read()
		journal = relpath(journal, args.directory)
		for line_number, line in enumerate(text.splitlines(), start=1):
			if DATE_REGEX.match(line):
				tag = line[:10]
				tags[tag] = (tag, journal, line_number)
	with open(tags_file, "w") as fd:
		fd.write("\n".join("{}\t{}\t{}".format(*tag) for tag in sorted(tags.values())) + "\n")
	with open(cache_file, "w") as fd:
		fd.write("\n\n".join(sorted(entries.values())))

elif args.action == "verify":
	errors = []
	dates = set()
	prev_indent = 0
	long_dates = None
	for journal in journal_files:
		with open(journal, "r") as fd:
			text = fd.read()
		for line_number, line in enumerate(text.splitlines(), start=1):
			if not line:
				continue
			indent = len(re.match("\t*", line).group(0))
			if indent == 0 and line[0] == " ":
				errors.append((journal, line_number, "non-tab indentation"))
				indent = len(re.match(" *", line).group(0))
			if indent - prev_indent > 1:
				errors.append((journal, line_number, "indentation"))
			if line and line[-1] in ("\t", " "):
				errors.append((journal, line_number, "end of line whitespace"))
			if re.search("\t ", line):
				errors.append((journal, line_number, "mixed tab/space indentation"))
			if re.search("[^\t]\t", line):
				errors.append((journal, line_number, "mid-line tab"))
			if re.search("[^ -~\t]", line):
				errors.append((journal, line_number, "non-ASCII characters"))
			line = line.strip()
			if not line.startswith("|") and "  " in line:
				errors.append((journal, line_number, "multiple spaces"))
			if indent == 0:
				if DATE_REGEX.match(line):
					cur_date = datetime.strptime(line[:10], "%Y-%m-%d")
					if long_dates is None:
						long_dates = (len(line) > 10)
					if long_dates != (len(line) > 10):
						errors.append((journal, line_number, "inconsistent date format"))
					if len(line) > 10 and line != cur_date.strftime("%Y-%m-%d, %A"):
						errors.append((journal, line_number, "date correctness"))
					if cur_date in dates:
						errors.append((journal, line_number, "duplicate dates"))
					dates.add(cur_date)
				else:
					errors.append((journal, line_number, "indentation"))
			prev_indent = indent
	if errors:
		print("\n".join("{}:{}: {}".format(*error) for error in errors))
	for key, value in entries.items():
		if value.count('"') % 2:
			errors.append(("odd quotation marks", datetime.strptime(key, "%Y-%m-%d"), re.sub("^.*\n", "", value)))
