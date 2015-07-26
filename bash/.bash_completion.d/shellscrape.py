#!/usr/bin/env python3

import re
from argparse import ArgumentParser
from collections import Counter, defaultdict
from os import getcwd as pwd
from os.path import expanduser, realpath
from sys import argv

SHELL_HISTORY = realpath(expanduser("~/Dropbox/personal/documents/shell_history"))

KEYWORDS = ("if", "while", "for", "then", "do")

LONG_SHORT_OPTIONS = ("find", "java")

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
    with open(SHELL_HISTORY) as fd:
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

def operation_analyze():
    history = read_history()
    # program -> (option -> values)
    option_values = defaultdict((lambda: defaultdict(Counter)))
    for command in history:
        program = command.split()[0]
        if program in LONG_SHORT_OPTIONS:
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
            if None in counter:
                option_types[program][option] = "none"
            else:
                option_types[program][option] = "argument"
    for program, options in sorted(option_types.items()):
        print(program)
        for option, argument_type in sorted(options.items()):
            print("    {}: {}".format(option, argument_type))


def operation_list():
    history = read_history()
    print("\n".join(sorted(set(command.split()[0] for command in history))))

def operation_complete(context):
    history = read_history()
    # find a line that begins with context
    results = set(command for command in history if command.startswith(context))
    # remove context from results, leaving the last word
    context_length = max(context.rfind(" "), context.rfind("\t"))
    results = set(command[context_length+1:] for command in results)
    # remove all subsequent words from results
    results = set(re.sub("[ \t].*", "", command) for command in results)
    print("\n".join(sorted(results)))

def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("context", nargs="?")
    args = arg_parser.parse_args()
    if args.context is None:
        operation_list()
    elif args.context[-1] != " ":
        operation_complete(args.context)

if __name__ == "__main__":
    main()
    #operation_analyze()
