#!/usr/bin/env python3

import re
import sys
from argparse import ArgumentParser


def read_all_inputs(files):
    if files:
        result = []
        for input_file in files:
            with open(input_file) as fd:
                result.append(fd.read())
        return '\n'.join(
            line for line in '\n'.join(result).splitlines()
            if line.strip()
        )
    elif not sys.stdin.isatty():
        return sys.stdin.read()
    else:
        return ''


def determine_indent(text):
    indent = ''
    for line in text.splitlines():
        match = re.match(r'\s*', text).group()
        if '\t' in match and ' ' in match:
            raise ValueError(f'both tabs and spaces in: {line.strip()}')
        if not indent:
            indent = match
        elif indent == '\t':
            if ' ' in match:
                raise ValueError(f'mixed indentation in: {line.strip()}')
            indent = '\t'
        elif len(match) % len(indent) != 0:
            indent = len(match) % len(indent)
    return indent


def get_indent(line, indent):
    count = 0
    while line.startswith(indent):
        count += 1
        line = line[len(indent):]
    return count


def sort_indented(text, depth):

    def add_items(result, items, item):
        if item:
            items.append(item)
        for item in sorted(items, key='\n'.join):
            result.extend(item)

    indent = determine_indent(text)
    result = []
    items = []
    item = []
    for line in text.splitlines():
        line_indent = get_indent(line, indent)
        if line_indent < depth:
            add_items(result, items, item)
            result.append(line)
            items = []
            item = []
        elif line_indent == depth:
            if item:
                items.append(item)
            item = [line]
        else:
            item.append(line)
    add_items(result, items, item)
    return '\n'.join(result)


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('files', nargs='*')
    arg_parser.add_argument('-d', '--depth', type=int, default=0)
    args = arg_parser.parse_args()
    print(sort_indented(
        read_all_inputs(args.files),
        args.depth,
    ))


if __name__ == '__main__':
    main()
