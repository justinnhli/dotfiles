#!/usr/bin/env python3
"""Script to clean shell history logs."""

import sys
from argparse import ArgumentParser, FileType
from collections import namedtuple

Event = namedtuple('Event', ('date', 'machine', 'pwd', 'command'))

def events_differ(event1, event2):
    """Check if two events are different.

    Arguments:
        event1 (Event): The first event.
        event2 (Event): The second event.

    Returns:
        bool: True if the events are different.
    """
    return any(
        getattr(event1, attr) != getattr(event2, attr)
        for attr in ['machine', 'pwd', 'command']
    )

def clean_shell_history(fd):
    """Remove duplicate shell history logs.

    Arguments:
        fd (FileObject): An open file, or stdin.

    Yields:
        str: The log with duplicate events removed.
    """
    last_event = None
    for line in fd:
        fields = line.strip().split('\t', maxsplit=3)
        if len(fields) != 4:
            continue
        event = Event(*fields)
        if last_event is None or events_differ(last_event, event):
            yield '\t'.join((event.date, event.machine, event.pwd, event.command))
            last_event = event

def main():
    """Run CLI."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin)
    args = arg_parser.parse_args()
    for line in clean_shell_history(args.infile):
        print(line)

if __name__ == '__main__':
    main()
