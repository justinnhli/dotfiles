#!/usr/bin/env python3

import re
import tarfile
from argparse import ArgumentParser
from datetime import datetime, timedelta
from os import chdir as cd, chmod, execvp, fork, listdir as ls, remove as rm, wait
from os.path import basename, exists as file_exists, expanduser, realpath
from stat import S_IRUSR
from string import punctuation
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
group.add_argument("-T",           dest="action",          action="store_const",  const="tag",      help="create tags file")
group.add_argument("-V",           dest="action",          action="store_const",  const="verify",   help="verify journal sanity")
group = arg_parser.add_argument_group("INPUT OPTIONS")
group.add_argument("--directory",  dest="directory",       action="store",                          help="use journal files in directory")
group.add_argument("--ignore",     dest="ignores",         action="append",                         help="ignore specified file")
group = arg_parser.add_argument_group("FILTER OPTIONS (APPLIES TO -[CGLS])")
group.add_argument("-d",           dest="date_range",      action="store",                          help="only use entries in range")
group.add_argument("-i",           dest="case_sensitive",  action="store_const",  const=False,      help="case insensitive match")
group.add_argument("-n",           dest="num_results",     action="store",        type=int,         help="max number of results")
group.add_argument("-p",           dest="punctuation",     action="store_const",  const=False,      help="do not match punctuation")
group = arg_parser.add_argument_group("OUTPUT OPTIONS")
group.add_argument("-r",           dest="reverse",         action="store_true",                     help="reverse chronological order")
args = arg_parser.parse_args()

if args.date_range and not all(dr and RANGE_REGEX.match(dr) for dr in args.date_range.split(",")):
	arg_parser.error("argument -d: '{}' should be in format [YYYY[-MM[-DD]]][:][YYYY[-MM[-DD]]][,...]".format(args.date_range))
if not stdin.isatty() and args.action in ("archive", "tag", "verify"):
	arg_parser.error("argument -[ATV]: operation can only be performed on files")
args.directory = realpath(expanduser(args.directory))
args.ignores = set(realpath(expanduser(path)) for path in args.ignores)

if stdin.isatty():
	file_entries = []
	journal_files = sorted(set("{}/{}".format(args.directory, f) for f in ls(args.directory) if f.endswith(".journal")) - args.ignores)
	for journal in journal_files:
		with open(journal, "r") as fd:
			file_entries.append(fd.read().strip())
	raw_entries = "\n\n".join(file_entries)
else:
	raw_entries = stdin.read()
if not raw_entries:
	arg_parser.error("no journal entries found or specified")
entries = dict((entry[:10], entry.strip()) for entry in raw_entries.strip().split("\n\n") if entry and DATE_REGEX.match(entry))

selected = set(entries.keys())
trans_table = str.maketrans("", "", punctuation)
for term in args.terms:
	if args.punctuation:
		selected = set(k for k in selected if re.search(term, entries[k], flags=args.case_sensitive|re.MULTILINE))
	else:
		term = term.translate(trans_table)
		selected = set(k for k in selected if re.search(term, entries[k].translate(trans_table), flags=args.case_sensitive|re.MULTILINE))
if selected and args.date_range:
	first_date = min(selected)
	last_date = (datetime.strptime(max(selected), "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
	for date_range in args.date_range.split(","):
		if ":" in date_range:
			start_date, end_date = date_range.split(":")
			start_date, end_date = (start_date or first_date, end_date or last_date)
			start_date += "-01" * int((10 - len(start_date)) / 2)
			end_date += "-01" * int((10 - len(end_date)) / 2)
			selected = set(k for k in selected if (start_date <= k < end_date))
		else:
			selected = set(k for k in selected if k.startswith(date_range))
selected = sorted(selected, reverse=args.reverse)
if args.num_results > 0:
	selected = selected[:args.num_results]

if args.action == "archive":
	filename = "jrnl{}".format(datetime.now().strftime("%Y%m%d%H%M%S"))
	with tarfile.open("{}.tbz".format(filename), "w:bz2") as tar:
		tar.add(args.directory, arcname=filename, filter=(lambda tarinfo: None if basename(tarinfo.name).startswith(".") else tarinfo))
		tar.add(argv[0], arcname="{}/{}".format(filename, basename(argv[0])))

elif args.action == "count" and selected:
	col_headers = ("YEAR", "POSTS", "WORDS", "MAX", "MEAN", "FREQ")
	row_headers = sorted(set(k[:4] for k in selected), reverse=args.reverse)
	sections = list(tuple(k for k in selected if k.startswith(year)) for year in row_headers)
	table = []
	for year, dates in zip(row_headers + ["all",], sections + [selected,]):
		posts = len(dates)
		lengths = tuple(len(entries[date].split()) for date in dates)
		words = sum(lengths)
		longest = max(lengths)
		mean = round(words / posts)
		freq = ((datetime.strptime(dates[-1], "%Y-%m-%d") - datetime.strptime(dates[0], "%Y-%m-%d")).days + 1) / posts
		table.append((year, str(posts), format(words, ",d"), str(longest), str(mean), "{:.3f}".format(freq)))
	widths = list(max(len(row[col]) for row in ([col_headers,] + table)) for col in range(0, len(col_headers)))
	print("  ".join(col.center(widths[i]) for i, col in enumerate(col_headers)))
	print("  ".join(width * "-" for width in widths))
	print("\n".join("  ".join(col.rjust(widths[i]) for i, col in enumerate(row)) for row in table))

elif args.action == "graph" and selected:
	print('digraph {')
	print('\tgraph [size="48", model="subset", rankdir="{}"];'.format('TB' if args.reverse else 'BT'))
	print()
	print('\t// NODES')
	print('\tnode [fontcolor="#4E9A06", shape="none"];')
	print('\n'.join('\t"{}" [fontsize="{}"];'.format(node, len(entries[node].split()) / 100) for node in selected))
	print()
	print('\t// EDGES')
	print('\tedge [color="#555753"];')
	ancestors = {}
	for src in sorted(selected):
		dests = set(dest for dest in REF_REGEX.findall(entries[src]) if src > dest and dest in selected)
		ancestors[src] = set().union(*(ancestors.get(parent, set()) for parent in dests))
		for dest in sorted(dests - ancestors[src], reverse=args.reverse):
			print('\t"{}" -> "{}";'.format(src, dest))
		ancestors[src] |= dests
	print('}')

elif args.action == "list" and selected:
	print("\n".join(selected))

elif args.action == "show" and selected:
	searchlog = "{}/log".format(args.directory)
	if file_exists(searchlog):
		command = ["-S",]
		if args.case_sensitive:
			command.append("i")
		if args.reverse:
			command.append("r")
		if args.date_range:
			command.append("d {} -".format(args.date_range))
		if args.num_results:
			command.append("n {} -".format(args.num_results))
		with open(searchlog, "a") as fd:
			fd.write("{}\t{} {}\n".format(datetime.today().isoformat(" "), re.sub(" -$", "", "".join(command)), " ".join('"{}"'.format(term) for term in args.terms)))
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

elif args.action == "tag":
	tags = {}
	for journal in journal_files:
		base_name = basename(journal)
		with open(journal, "r") as fd:
			text = fd.read()
		for line_number, line in enumerate(text.splitlines(), start=1):
			if DATE_REGEX.match(line):
				tag = line[:10]
				tags[tag] = (tag, base_name, line_number)
	tags_path = "{}/tags".format(args.directory)
	if file_exists(tags_path):
		rm(tags_path)
	with open(tags_path, "w") as fd:
		fd.write("\n".join("{}\t{}\t{}".format(*tag) for tag in sorted(tags.values())) + "\n")

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
