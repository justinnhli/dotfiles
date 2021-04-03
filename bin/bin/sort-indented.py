#!/usr/bin/env python3

import re
from argparse import ArgumentParser, FileType


def read_all_inputs(files):
    contents = [fd.read() for fd in files]
    return '\n'.join(
        line for line in '\n'.join(contents).splitlines()
        if line.strip()
    )


def determine_indent(text):
    indent = ''
    for line in text.splitlines():
        match = re.match(r'\s*', line).group()
        if '\t' in match and ' ' in match:
            raise ValueError(f'both tabs and spaces in: {line.strip()}')
        if not indent:
            indent = match
        elif indent == '\t':
            if ' ' in match:
                raise ValueError(f'mixed indentation in: {line.strip()}')
            indent = '\t'
        elif len(match) % len(indent) != 0:
            indent = (len(match) % len(indent)) * ' '
    return indent


def min_indent(text, indent):
    return min(
        (
            len(re.findall(indent, line[:re.search(r'[^\s]', line).start()]))
            for line in text.splitlines() if line.strip()
        ),
        default=0,
    )


def get_indent(line, indent):
    count = 0
    while line.startswith(indent):
        count += 1
        line = line[len(indent):]
    return count


def sort_indented(text, depth=None, reverse=False):

    def add_items(result, items, item):
        if item:
            items.append(item)
        for item in sorted(items, key='\n'.join, reverse=reverse):
            result.extend(item)

    indent = determine_indent(text)
    if depth is None:
        depth = min_indent(text, indent)
    assert indent != ''
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
    arg_parser.add_argument('files', nargs='*', type=FileType(), default=[FileType()('-')], help='')
    arg_parser.add_argument('-d', dest='depth', type=int, help='the depth of the indent to sort by')
    arg_parser.add_argument('-r', dest='reverse', action='store_true', help='sort in reverse order')
    args = arg_parser.parse_args()
    print(sort_indented(
        read_all_inputs(args.files),
        depth=args.depth,
        reverse=args.reverse,
    ))


if __name__ == '__main__':
    main()
