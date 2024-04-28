#!/usr/bin/env python3

"""
anything that begins with - can be assumed to be an option (except --)
for each option, either:
* it takes no arguments
* it takes arguments from a fixed set of options
* it takes arguments from filenames
for now, assume program is only context
can then build a per program dictionary of options, then try to classify them
* first, figure out whether arguments are needed
* short options that are followed by other short options don't have arguments
* ditto long options that are followed by other long options
* long options with = need arguments
* short options with arguments, followed by other short options, also need arguments
* for options with arguments, use 80/20 analysis (do 20% of the options account for 80% of the usage?)

other difficulties:
* non-dash options (eg. git)
* single-dash long-options (eg. java)
"""

import re
from argparse import ArgumentParser
from ast import literal_eval
from collections import Counter, defaultdict
from os import listdir
from os.path import exists as file_exists, join as join_path, expanduser, realpath

SHELL_HISTORY = realpath(expanduser("~/Dropbox/personal/logs/shistory"))
COMPLETION_FILE = realpath(expanduser("~/.bash_completion.d/completions.dict"))

KEYWORDS = ("if", "while", "for", "then", "do")

LONG_SHORT_OPTIONS = ("find", "java")

USAGE_THRESHOLD = 5

def is_weird(command):
    weird = False
    # check for unbalanced parentheses
    weird |= (command.count("(") != command.count(")"))
    # check for unbalanced quotes
    weird |= (command.count("'") % 2 != 0)
    weird |= (command.count('"') % 2 != 0)
    # check for escape sequences (mostly for spaces in paths)
    weird |= (command.count("\\") != 0)
    # check for environmental variables
    weird |= ((re.match("[^ ]*=", command)) is not None)
    # check for nested shells
    # TODO eventually these should be extracted and used
    weird |= (command.count("$(") != 0)
    weird |= (command.count("<(") != 0)
    return weird

def read_history():
    history = set()
    if file_exists(SHELL_HISTORY):
        for shistory in listdir(SHELL_HISTORY):
            if not shistory.endswith('.shistory'):
                continue
            with open(join_path(SHELL_HISTORY, shistory)) as fd:
                for entry in fd.readlines():
                    # only take COMMAND from 'DATE HOST PWD COMMAND'
                    entry = entry.strip().split("\t", maxsplit=3)[-1].strip()
                    for line in entry.split(";"):
                        for conjunction in line.split("|"):
                            for command in conjunction.split("&&"):
                                if not is_weird(command) and len(command.split()) > 0:
                                    history.add(command.strip())
        # filter out commands that begin with shell keywords
        history = set(command for command in history if command.split()[0] not in KEYWORDS)
        # filter out commands that begin with non-alphabet characters
        history = set(command for command in history if re.match("[a-z]", command))
    return history

def simplify_command(command):
    # remove all quoted expressions
    transformed = command
    for match in re.finditer("'[^']*'", command):
        transformed = transformed.replace(match.group(), re.sub("[ \t]", "_", match.group()))
    command = transformed
    transformed = command
    for match in re.finditer('"[^\\"]*"', command):
        transformed = transformed.replace(match.group(), re.sub("[ \t]", "_", match.group()))
    command = transformed
    # remove anything with /, ., *, or ~
    #command = re.sub(" [^ ]*(/[^ ]*)/*", "", command)
    #command = re.sub(" [^ ]*(\\.[^ ]*)\\.*", "", command)
    #command = re.sub(" [^ ]*(\\*[^ ]*)\\**", "", command)
    #command = re.sub(" [^ ]*(~[^ ]*)~*", "", command)
    # remove all input/output redirections
    command = re.sub(" +>>?.*", "", command)
    command = re.sub(" [^ ]*([<>][^ ]*)[<>]*", "", command)
    # turn --option=value into --option value
    command = re.sub("( -[^=]+)=([^ ]*)", "\\g<1> \\g<2>", command)
    return command

def operation_analyze(program, history):
    # program -> (option -> values)
    option_values = defaultdict((lambda: defaultdict(Counter)))
    for command in history:
        if command.split()[0] in LONG_SHORT_OPTIONS:
            continue
        if command.split()[0] != program:
            continue
        command = simplify_command(command)
        previous_option = None
        for index, argument in enumerate(command.split()):
            if argument[0] == "-":
                # new option
                if len(argument) == 1 or argument == "--" or re.search("[^0-9A-Za-z-]", argument[1:]):
                    previous_option = None
                    continue
                if argument[1] != "-" and re.match("^[0-9A-Za-z-]*$", argument[1:]):
                    # [conjunction of] short options
                    for letter in argument[1:-1]:
                        option_values[program]["-" + letter].update([None,])
                    argument = "-" + argument[-1]
                if previous_option is not None:
                    # previous option had no argument
                    option_values[program][previous_option].update([None,])
                if index == len(command.split()) - 1:
                    option_values[program][argument].update([None,])
                previous_option = argument
            elif previous_option is not None:
                # potential argument for previous option
                option_values[program][previous_option].update([argument,])
                previous_option = None
    option_types = defaultdict(dict)
    for program, options in sorted(option_values.items()):
        for option, counter in sorted(options.items()):
            if sum(counter.values()) < USAGE_THRESHOLD:
                continue
            if None in counter:
                option_types[program][option] = "none"
            else:
                option_types[program][option] = "argument"
    return option_types

def read_completions():
    completions = {}
    if file_exists(COMPLETION_FILE):
        with open(COMPLETION_FILE) as fd:
            completions = literal_eval("{" + fd.read() + "}")
    return completions

def operation_update():
    history = read_history()
    completions = {}
    for program in sorted(set(command.split()[0] for command in history)):
        suggestions = set()
        for option in operation_analyze(program, history)[program].keys():
            if option.startswith("-"):
                suggestions.add(option)
        if suggestions:
            completions[program] = sorted(suggestions)
    with open(COMPLETION_FILE, "w") as fd:
        fd.write("\n".join("\"{}\": {},".format(program, options) for program, options in sorted(completions.items())))

def operation_list():
    print("\n".join(sorted(read_completions().keys())))

def operation_complete(pwd, context):
    words = context.strip().split()
    if len(words) > 1:
        program = words[0]
        last_word = words[-1]
        completions = read_completions()
        if program in completions:
            print("\n".join(completion for completion in completions[program] if completion.startswith(last_word)))

def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("pwd", nargs="?")
    arg_parser.add_argument("context", nargs="?")
    arg_parser.add_argument("--update", action="store_true", default=False)
    args = arg_parser.parse_args()
    if args.update:
        operation_update()
    elif args.context is None:
        operation_list()
    else:
        operation_complete(args.pwd, args.context)

if __name__ == "__main__":
    main()
