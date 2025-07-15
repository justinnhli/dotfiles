#!/usr/bin/env python3
"""Sort the input by the text at the indent level."""

import re
from sys import stdin
from argparse import ArgumentParser, FileType


def determine_indent(text):
    # type: (str) -> str
    """Determine the indent string of a string."""
    indent = ''
    for line in text.splitlines():
        match = re.match(r'\s*', line).group()
        if '\t' in match and ' ' in match:
            raise ValueError(f'line contains both tabs and spaces in: {line.strip()}')
        if ('\t' in indent and ' ' in match) or ('\t' in match and ' ' in indent):
            raise ValueError('input contains both tabs and spaces')
        if not indent:
            indent = match
        elif len(match) % len(indent) != 0:
            indent = (len(match) % len(indent)) * indent[0]
    return indent


def min_indent(text, indent):
    # type: (str, str) -> int
    """Determine the minimum indent of the input."""
    return min(
        (
            len(re.findall(indent, line[:re.search(r'[^\s]', line).start()]))
            for line in text.splitlines() if line.strip()
        ),
        default=0,
    )


def get_indent(line, indent):
    # type: (str, str) -> int
    """Determine the indent of a line."""
    count = 0
    while line.startswith(indent):
        count += 1
        line = line[len(indent):]
    return count


def sort_indented(text, depth=None, reverse=False):
    # type: (str, int, bool) -> str
    """Sort the input by the text at the indent level."""

    def add_items(result, items, item):
        if item:
            items.append(item)
        for child_items in sorted(items, key='\n'.join, reverse=reverse):
            result.extend(child_items)

    indent = determine_indent(text)
    if depth is None:
        depth = min_indent(text, indent)
    assert indent != ''
    result = [] # type: list[str]
    items = [] # type: list[list[str]]
    item = [] # type: list[str]
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
    # type: () -> None
    """Provide a CLI entry point."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument('inputfile', nargs='?', type=FileType('r'), default=stdin)
    arg_parser.add_argument('-d', dest='depth', type=int, help='the depth of the indent to sort by')
    arg_parser.add_argument('-r', dest='reverse', action='store_true', help='sort in reverse order')
    args = arg_parser.parse_args()
    print(sort_indented(
        args.inputfile.read(),
        depth=args.depth,
        reverse=args.reverse,
    ))


if __name__ == '__main__':
    main()
