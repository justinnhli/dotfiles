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
	arg_parser = ArgumentParser(usage="%(prog)s <operation> [options] [TERM ...]")
	arg_parser.set_defaults(directory="./", ignores=["~/journal/notes.journal",], ignore_case=True, num_results="0", reverse=False)
	arg_parser.add_argument("terms",  metavar="TERM", nargs="*", help="pattern which must exist in entries")
	group = arg_parser.add_argument_group("OPERATIONS")
	group.add_argument("-A",  dest="action",  action="store_const",  const="archive",  help="archive to datetimed tarball")
	group.add_argument("-C",  dest="action",  action="store_const",  const="count",    help="count words and entries")
	group.add_argument("-G",  dest="action",  action="store_const",  const="graph",    help="graph entry references in DOT")
	group.add_argument("-L",  dest="action",  action="store_const",  const="list",     help="list entry dates")
	group.add_argument("-S",  dest="action",  action="store_const",  const="show",     help="show entries")
	group.add_argument("-T",  dest="action",  action="store_const",  const="tag",      help="create tags file")
	group.add_argument("-V",  dest="action",  action="store_const",  const="verify",   help="verify journal sanity")
	group = arg_parser.add_argument_group("INPUT OPTIONS")
	group.add_argument("--directory",  dest="directory",   action="store",   help="use journal files in directory")
	group.add_argument("--ignore",     dest="ignores",     action="append",  help="ignore specified files")
	group = arg_parser.add_argument_group("OUTPUT OPTIONS")
	group.add_argument("-d",  dest="date_range",   action="store",        help="only use entries in range")
	group.add_argument("-i",  dest="ignore_case",  action="store_false",  help="ignore ignore case")
	group.add_argument("-n",  dest="num_results",  action="store",        help="max number of results")
	group.add_argument("-r",  dest="reverse",      action="store_true",   help="reverse chronological order")
	args = arg_parser.parse_args()

	errors = []
	if not args.action:
		errors.append("no operation specified")
	if args.date_range and not all(RANGE_REGEX.match(dr) for dr in args.date_range.split(",")):
		errors.append("option -d/--date must be of the form [YYYY[-MM[-DD]]][:][YYYY[-MM[-DD]]][,...]")
	if not args.num_results.isdigit():
		errors.append("option -n/--num-results must be an integer")
	if errors:
		print("\n".join("Error: {}".format(error) for error in errors) + "\n")
		arg_parser.print_help()
		exit(1)
	args.directory = realpath(expanduser(args.directory))
	args.ignores = set(realpath(expanduser(path)) for path in args.ignores)
	args.ignore_case = re.IGNORECASE if args.ignore_case else 0
	args.num_results = int(args.num_results)

	if stdin.isatty():
		file_entries = []
		for journal in sorted(set("{}/{}".format(args.directory, f) for f in ls(args.directory) if f.endswith(".journal")) - args.ignores):
			with open(journal, "r") as fd:
				file_entries.append(fd.read().strip())
		raw_entries = "\n\n".join(file_entries)
	else:
		raw_entries = stdin.read()
	if not raw_entries:
		errors.append("Error: no journal files found or specified")
		exit(1)
	entries = dict((entry[:10], entry.strip()) for entry in raw_entries.strip().split("\n\n") if entry and DATE_REGEX.match(entry))

	selected = set(entries.keys())
	for term in args.terms:
		selected -= set(k for k in selected if not re.search(term, entries[k], flags=args.ignore_case))
	if selected and args.date_range:
		all_dates = selected
		selected = set()
		for date_range in args.date_range.split(","):
			first_date = min(all_dates)
			last_date = max(all_dates)
			if ":" in date_range:
				start_date, end_date = date_range.split(":")
				start_date, end_date = (start_date or first_date, end_date or last_date)
				start_date += "-01" * int((10 - len(start_date)) / 2)
				end_date += "-01" * int((10 - len(end_date)) / 2)
				selected |= set(k for k in all_dates if (start_date < k and k <= end_date))
			else:
				selected |= set(k for k in all_dates if k.startswith(date_range))
	selected = sorted(selected, reverse=args.reverse)
	if args.num_results > 0:
		selected = selected[:args.num_results]

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

	elif args.action == "count":
		first_date_str = selected[0]
		first_date = Datetime.strptime(first_date_str, "%Y-%m-%d")
		last_date_str = selected[-1]
		last_date = Datetime.strptime(last_date_str, "%Y-%m-%d")
		header = ("year", "posts", "words", "max", "mean", "freq")
		table = []
		length = 4
		for unit in sorted(set(key[:length] for key in selected), reverse=args.reverse):
			dates = list(date for date in selected if date[:length] == unit)
			posts = len(dates)
			lengths = list(len(entries[date].split()) for date in dates)
			words = sum(lengths)
			longest = max(lengths)
			mean = round(words / posts)
			last_unit_date = (last_date if last_date_str[:length] == unit else Datetime(int(unit), 12, 31))
			first_unit_date = (first_date if first_date_str[:length] == unit else Datetime(int(unit), 1, 1))
			freq = "{:.3f}".format(((last_unit_date - first_unit_date).days + 1) / posts)
			table.append((unit, posts, words, longest, mean, freq))
		total = ["total"] + [sum(row[col] for row in table[1:]) for col in range(1, 3)]
		total.extend([max(row[3] for row in table[1:]), round(total[2] / total[1]), "{:.3f}".format(((last_date - first_date).days + 1) / total[1])])
		table.append(tuple(total))
		table = list((year, posts, format(words, ",d"), maxx, mean, freq) for year, posts, words, maxx, mean, freq in table)
		widths = list(max(len(str(row[col])) for row in ([header,] + table)) for col in range(0, 6))
		print("  ".join(col.center(widths[i]) for i, col in enumerate(header)).upper())
		print("  ".join(width * "-" for width in widths))
		for row in table:
			print("  ".join(str(col).rjust(widths[i]) for i, col in enumerate(row)))

	elif args.action == "graph":
		ref_map = {}
		for key_date in selected:
			for reference in REF_REGEX.findall(entries[key_date]):
				if reference != key_date and reference in selected:
					ref_map.setdefault(reference, set())
					ref_map[reference].add(key_date[:10])
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

	elif args.action == "list":
		print("\n".join(selected))

	elif args.action == "show" and selected:
		text = "\n\n".join(entries[key] for key in selected)
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
