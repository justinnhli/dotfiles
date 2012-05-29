#!/usr/bin/env python3

import re
from argparse import ArgumentParser
from datetime import datetime as Datetime
from os import chdir as cd, chmod, execvp, fork, getcwd as pwd, listdir as ls, remove as rm, system, wait
from os.path import exists as file_exists, expanduser, realpath, relpath
from shutil import copy as cp, copytree, ignore_patterns, rmtree
from stat import S_IRUSR
from sys import stdin, stdout, argv
from tempfile import mkdtemp, mkstemp

DATE_REGEX = re.compile("([0-9]{4}-[0-9]{2}-[0-9]{2})(, (Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day)?")
BIB_REGEX = re.compile("@[a-z]*{(.*),$")
RANGE_REGEX = re.compile("^([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?:?([0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?)?$")
REF_REGEX = re.compile("([0-9]{4}-[0-9]{2}-[0-9]{2})")

def main():
	arg_parser = ArgumentParser(usage="%(prog)s <operation> [options] [TERM ...]", description="a command line tool for viewing and maintaining a journal")
	arg_parser.set_defaults(directory="./", ignores=[], ignore_case=True, num_results=0, reverse=False)
	arg_parser.add_argument("terms",  metavar="TERM", nargs="*", help="pattern which must exist in entries")
	group = arg_parser.add_argument_group("OPERATIONS")
	group = group.add_mutually_exclusive_group(required=True)
	group.add_argument("-A",           dest="action",       action="store_const",  const="archive",  help="archive to datetimed tarball")
	group.add_argument("-C",           dest="action",       action="store_const",  const="count",    help="count words and entries")
	group.add_argument("-G",           dest="action",       action="store_const",  const="graph",    help="graph entry references in DOT")
	group.add_argument("-L",           dest="action",       action="store_const",  const="list",     help="list entry dates")
	group.add_argument("-S",           dest="action",       action="store_const",  const="show",     help="show entry contents")
	group.add_argument("-T",           dest="action",       action="store_const",  const="tag",      help="create tags file")
	group.add_argument("-V",           dest="action",       action="store_const",  const="verify",   help="verify journal sanity")
	group = arg_parser.add_argument_group("INPUT OPTIONS")
	group.add_argument("--directory",  dest="directory",    action="store",                          help="use journal files in directory")
	group.add_argument("--ignore",     dest="ignores",      action="append",                         help="ignore specified file")
	group = arg_parser.add_argument_group("FILTER OPTIONS (APPLY TO -C, -G, -L, and -S)")
	group.add_argument("-d",           dest="date_range",   action="store",                          help="only use entries in range")
	group.add_argument("-i",           dest="ignore_case",  action="store_false",                    help="ignore ignore case")
	group.add_argument("-n",           dest="num_results",  action="store",        type=int,         help="max number of results")
	group.add_argument("-r",           dest="reverse",      action="store_true",                     help="reverse chronological order")
	args = arg_parser.parse_args()

	if args.date_range and not all(dr and RANGE_REGEX.match(dr) for dr in args.date_range.split(",")):
		arg_parser.error("argument -d: '{}' should be in format [YYYY[-MM[-DD]]][:][YYYY[-MM[-DD]]][,...]".format(args.date_range))
	args.directory = realpath(expanduser(args.directory))
	args.ignores = set(realpath(expanduser(path)) for path in args.ignores)
	args.ignore_case = re.IGNORECASE if args.ignore_case else 0

	if stdin.isatty():
		file_entries = []
		for journal in sorted(set("{}/{}".format(args.directory, f) for f in ls(args.directory) if f.endswith(".journal")) - args.ignores):
			with open(journal, "r") as fd:
				file_entries.append(fd.read().strip())
		raw_entries = "\n\n".join(file_entries)
	else:
		raw_entries = stdin.read()
	if not raw_entries:
		arg_parser.error("no journal files found or specified")
	entries = dict((entry[:10], entry.strip()) for entry in raw_entries.strip().split("\n\n") if entry and DATE_REGEX.match(entry))

	selected = set(entries.keys())
	for term in args.terms:
		selected -= set(k for k in selected if not re.search(term, entries[k], flags=args.ignore_case))
	if selected and args.date_range:
		all_dates = selected
		first_date = min(all_dates)
		last_date = max(all_dates)
		selected = set()
		for date_range in args.date_range.split(","):
			if ":" in date_range:
				start_date, end_date = date_range.split(":")
				start_date, end_date = (start_date or first_date, end_date or last_date)
				start_date += "-01" * int((10 - len(start_date)) / 2)
				end_date += "-01" * int((10 - len(end_date)) / 2)
				selected |= set(k for k in all_dates if (start_date <= k and k < end_date))
			else:
				selected |= set(k for k in all_dates if k.startswith(date_range))
	selected = sorted(selected, reverse=args.reverse)
	if args.num_results > 0:
		selected = selected[:args.num_results]

	searchlog = "{}/log".format(args.directory)
	if args.action in ("graph", "list", "show") and file_exists(searchlog):
		command = []
		if args.action == "graph":
			command.append("-G")
		elif args.action == "list":
			command.append("-L")
		elif args.action == "show":
			command.append("-S")
		if args.ignore_case != re.IGNORECASE:
			command.append("i")
		if args.reverse:
			command.append("r")
		if args.date_range:
			command.append("d {} -".format(args.date_range))
		if args.num_results:
			command.append("n {} -".format(args.num_results))
		with open(searchlog, "a") as fd:
			fd.write("{}\t{} {}\n".format(Datetime.today().isoformat(" "), re.sub(" -$", "", "".join(command)), "".join(args.terms)))

	if args.action == "archive":
		filename = "jrnl" + Datetime.now().strftime("%Y%m%d%H%M%S")
		temp_path = mkdtemp()
		copytree(args.directory, temp_path + "/" + filename, ignore=ignore_patterns(".*"))
		cp(argv[0], temp_path + "/" + filename)
		cur_path = pwd()
		cd(temp_path)
		command = "tar -jcvf {f}.tbz {f}".format(f=filename)
		print(command)
		system(command)
		cp(filename + ".tbz", cur_path)
		rmtree(temp_path)

	elif args.action == "count" and selected:
		col_headers = ("YEAR", "POSTS", "WORDS", "MAX", "MEAN", "FREQ")
		row_headers = sorted(set(k[:4] for k in selected), reverse=args.reverse) + ["total",]
		table = []
		sections = list(tuple(k for k in selected if k.startswith(year)) for year in row_headers[:-1]) + [selected,]
		for year, dates in zip(row_headers, sections):
			posts = len(dates)
			lengths = tuple(len(entries[date].split()) for date in dates)
			words = sum(lengths)
			longest = max(lengths)
			mean = round(words / posts)
			freq = ((Datetime.strptime(dates[-1], "%Y-%m-%d") - Datetime.strptime(dates[0], "%Y-%m-%d")).days + 1) / posts
			table.append((year, str(posts), format(words, ",d"), str(longest), str(mean), "{:.3f}".format(freq)))
		widths = list(max(len(row[col]) for row in ([col_headers,] + table)) for col in range(0, len(col_headers)))
		print("  ".join(col.center(widths[i]) for i, col in enumerate(col_headers)))
		print("  ".join(width * "-" for width in widths))
		for row in table:
			print("  ".join(col.rjust(widths[i]) for i, col in enumerate(row)))

	elif args.action == "graph" and selected:
		ref_map = {}
		for k in selected:
			for reference in REF_REGEX.findall(entries[k]):
				if reference != k and reference in selected:
					ref_map.setdefault(reference, set()).add(k[:10])
		print('digraph {')
		print('\tgraph [size="48", model="subset", rankdir="BT"];')
		print()
		print('\t// NODES')
		print('\tnode [fontcolor="#3465A4", shape="none"];')
		print('\n'.join('\t"{}" [fontsize="{}"];'.format(dest, len(entries[dest].split()) / 100) for dest in ref_map))
		print()
		print('\t// EDGES')
		print('\tedge [color="#888A85"];')
		for dest in ref_map:
			for src in ref_map[dest]:
				print('\t"{}" -> "{}";'.format(src, dest))
		print('}')

	elif args.action == "list" and selected:
		print("\n".join(selected))

	elif args.action == "show" and selected:
		text = "\n\n".join(entries[k] for k in selected)
		if stdout.isatty():
			temp_file = mkstemp(".journal")[1]
			with open(temp_file, "w") as fd:
				fd.write(text)
			chmod(temp_file, S_IRUSR)
			if fork() == 0:
				cd(args.directory)
				vim_args = ["vim", temp_file]
				if args.terms:
					if args.ignore_case:
						vim_args.extend(["-c", "set nosmartcase"])
					else:
						vim_args.extend(["-c", "set noignorecase"])
					vim_args.extend(["-c", "/\\v[^\t-~]|" + "|".join(("(" + term + ")") for term in args.terms)])
				vim_args.extend(["-c", ":set nocursorline", "-c", ":set nospell", "-c", ":0"])
				execvp("vim", vim_args)
			else:
				wait()
				rm(temp_file)
		else:
			print(text)

	elif args.action == "tag":
		if not stdin.isatty():
			print("Error: tags file can only be created if input is from files")
			exit(1)
		tags_path = args.directory + "/tags"
		tags = {}
		if file_exists(tags_path):
			rm(tags_path)
		for journal in (set("{}/{}".format(args.directory, f) for f in ls(args.directory) if f.endswith(".journal")) - args.ignores):
			with open(journal, "r") as fd:
				text = fd.read()
			for line_number, line in enumerate(text.split("\n")):
				if DATE_REGEX.match(line):
					tag = line[:10]
					tags[tag] = (tag, relpath(journal, args.directory), line_number + 1)
		for bibtex in (set("{}/{}".format(args.directory, f) for f in ls(args.directory) if f.endswith(".bib")) - args.ignores):
			with open(bibtex, "r") as fd:
				text = fd.read()
			for line_number, line in enumerate(text.split("\n")):
				match = BIB_REGEX.match(line)
				if match:
					tag = match.group(1)
					tags[tag] = (tag, relpath(bibtex, args.directory), line_number + 1)
		with open(tags_path, "w") as fd:
			fd.write("\n".join("{}\t{}\t{}".format(*tag) for tag in sorted(tags.values())))
			fd.write("\n")

	elif args.action == "verify":
		errors = []
		dates = set()
		last_indent = 0
		cur_date = Datetime(1, 1, 1)
		for line in raw_entries.split("\n"):
			if not line:
				continue
			indent = len(re.match("^\t*", line).group(0))
			if indent == 0 and line[0] == " ":
				errors.append(("non-tab indentation", cur_date, line))
				indent = len(re.match("^ *", line).group(0))
			if indent - last_indent > 2:
				errors.append(("indentation", cur_date, line))
			if line and line[-1] in ("\t", " "):
				errors.append(("end of line whitespace", cur_date, line))
			line = line.strip()
			if indent:
				if not line.startswith("|") and "  " in line:
					errors.append(("multiple space", cur_date, line))
				if line.count("\"") % 2:
					errors.append(("balanced quotes", cur_date, line))
				if re.search("[^ -~\t]", line):
					errors.append(("non-ASCII characters", cur_date, line))
			else:
				if not DATE_REGEX.match(line):
					errors.append(("indentation", cur_date, line))
				cur_date = Datetime.strptime(line[:10], "%Y-%m-%d")
				if len(line) > 10 and line != cur_date.strftime("%Y-%m-%d, %A"):
					errors.append(("date correctness", cur_date, line))
				if cur_date in dates:
					errors.append(("duplicate dates", cur_date, line))
				else:
					dates.add(cur_date)
			last_indent = indent
		if errors:
			print("\n".join("{} ({}): \"{}...\"".format(error, date.strftime("%Y-%m-%d"), line.strip()[:20]) for error, date, line in errors))

if __name__ == "__main__":
	main()
