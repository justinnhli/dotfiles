#!/usr/bin/env python3

import re
from os.path import expanduser, realpath
from collections import Counter, defaultdict
from math import log

SHELL_HISTORY = realpath(expanduser("~/Dropbox/personal/documents/shell_history"))

KEYWORDS = ["if", "while", "for"]

def read_shell_history():
    with open(SHELL_HISTORY) as fd:
        for log in fd.readlines():
            line = log.strip().split("\t", maxsplit=3)
            if len(line) == 4:
                yield(line[3].strip())

def is_weird(line):
    weird = False
    # check for unbalanced parentheses
    weird |= (line.count("(") != line.count(")"))
    # check for unbalanced quotes
    weird |= (line.count("'") % 2 != 0)
    weird |= (line.count('"') % 2 != 0)
    # check for escape sequences (mostly for spaces in paths)
    weird |= (line.count("\\") != 0)
    # check for environmental variables
    weird |= ((re.match("[^ ]*=", line)) is not None)
    # check for nested shells
    # TODO eventually these should be extracted and used
    weird |= (line.count("$(") != 0)
    weird |= (line.count("<(") != 0)
    return weird

def commands_from_line(line):
    commands = line.split("|")
    old_size = len(commands)
    new_size = -1
    while old_size != new_size:
        old_size = new_size
        new_commands = []
        for command in commands:
            new_commands.extend(command.split("&&"))
        commands = new_commands
        new_size = len(commands)
    return [command.strip() for command in commands if not is_weird(command)]

def simplify_command(command):
    # remove all quoted expressions
    command = re.sub("'[^']*'", "", command)
    command = re.sub('"[^\\"]*"', "", command)
    # remove anything with /, ., *, or ~
    command = re.sub(" [^ ]*(/[^ ]*)/*", "", command)
    command = re.sub(" [^ ]*(\\.[^ ]*)\\.*", "", command)
    command = re.sub(" [^ ]*(\\*[^ ]*)\\**", "", command)
    command = re.sub(" [^ ]*(~[^ ]*)~*", "", command)
    # remove all input/output redirections
    command = re.sub(" +>>?.*", "", command)
    command = re.sub(" [^ ]*([<>][^ ]*)[<>]*", "", command)
    # turn --option=value into --option value
    command = re.sub("( -[^=]+)=([^ ]*)", "\\g<1> \\g<2>", command)
    return command

def split_context(command):
    terms = command.split()
    context = []
    for term in terms:
        if not term.startswith("-"):
            context.append(term)
        else:
            break
    options = ["-" + term for term in " ".join(terms[len(context):]).split(" -") if term != ""]
    if len(options) > 0:
        options[0] = options[0][1:]
    return " ".join(context), options

def entropy(values):
    if len(values) == 1:
        return 1.0
    total = sum(values)
    proportions = [value / total for value in values]
    return sum(-p * log(p, 2) for p in proportions) / log(len(values), 2)

def _prune_by_entropy(path, counts):
    paths = []
    if len(counts) > 1:
        if len(path) > 0:
            e = entropy([value["__count"] for key, value in counts.items() if key != "__count"])
            if e < 0.9:
                paths.append(" ".join(path))
        for key, value in sorted(counts.items()):
            if key != "__count":
                paths.extend(_prune_by_entropy(path + [key,], value))
    return paths

def prune_by_entropy(contexts):
    counts = {}
    counts["__count"] = 0
    for context in contexts:
        level_count = counts
        for term in context.split():
            if term not in level_count:
                level_count[term] = {}
                level_count[term]["__count"] = 0
            level_count[term]["__count"] += 1
            level_count = level_count[term]
    return _prune_by_entropy([], counts)

def main():
    history = []
    for line in read_shell_history():
        commands = commands_from_line(line)
        for command in commands:
            command = simplify_command(command)
            if not command:
                continue
            program = command.split()[0]
            if re.match("[a-zA-Z0-9]", program) and program not in KEYWORDS:
                history.append(command)
    contexts = [split_context(command)[0] for command in history if " " in command]
    print(prune_by_entropy(contexts))
    exit()
    arguments = defaultdict(Counter)
    for command in history:
        if " " in command:
            context, options = split_context(command)
        else:
            context = command
            options = ""
        arguments[context].update(options)
    # TODO need to further break down the context to provide better tab completion
    for context, counter in sorted(arguments.items()):
        distinct = len(counter)
        if distinct == 0:
            continue
        total = sum(counter.values())
        average = total / distinct
        pairs = [pair for pair in counter.most_common() if pair[1] >= average]
        if len(pairs) == 0:
            continue
        """
        print(context)
        for key, count in sorted(pairs, key=(lambda pair: pair[1]), reverse=True):
            print("\t{}:{}".format(key, count))
            """

if __name__ == "__main__":
    main()
