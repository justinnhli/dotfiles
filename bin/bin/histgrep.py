#!/usr/bin/env python3
"""Grep through search history."""

import re
from argparse import ArgumentParser
from collections import namedtuple
from pathlib import Path

HISTORY_DIR = Path('~/Dropbox/personal/logs/shistory/').expanduser().resolve()

Event = namedtuple('Event', ('date', 'machine', 'pwd', 'command'))


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument('patterns', nargs='*')
    arg_parser.add_argument('-d', dest='date', action='store')
    arg_parser.add_argument('-u', dest='user', action='store')
    arg_parser.add_argument('-m', dest='machine', action='store')
    arg_parser.add_argument('-p', dest='pwd', action='store')
    args = arg_parser.parse_args()
    results = set()
    for history_file in sorted(HISTORY_DIR.glob('*.shistory')):
        with history_file.open() as fd:
            for line in fd:
                event = Event(*line.strip().split('\t', maxsplit=3))
                if args.date is not None and not re.search(args.date, event.date):
                    continue
                if args.user is not None and not re.search(args.user, event.machine):
                    continue
                if args.machine is not None and not re.search(args.machine, event.machine):
                    continue
                if args.pwd is not None and not re.search(args.pwd, event.machine):
                    continue
                if not all(re.search(pat, event.command) for pat in args.patterns):
                    continue
                results.add('\t'.join((event.date, event.machine, event.pwd, event.command)))
    print('\n'.join(sorted(results)))


if __name__ == '__main__':
    main()
