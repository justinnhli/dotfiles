#!/usr/bin/env python3

import re
from argparse import ArgumentParser
from collections import defaultdict
from itertools import chain
from pathlib import Path
from subprocess import run


PACMANS = [
    Path('/usr/bin/pikaur'),
    Path('/usr/bin/pacman'),
]


def find_pacman():
    # type: () -> str
    for pacman in PACMANS:
        if pacman.exists():
            return str(pacman)
    raise FileNotFoundError('could not find a pacman-equivalent command')


PACMAN = find_pacman()


IGNORE_PATTERNS = [
    re.compile(r'.*\.pem'),
    re.compile(r'.*\.un~'),
]


def should_ignore(path):
    # type: (Path) -> bool
    return any(pattern.fullmatch(path.name) for pattern in IGNORE_PATTERNS)


def get_modified_files():
    # type: () -> dict[str, set[Path]]
    process = run([PACMAN, '-Qii'], capture_output=True, check=True)
    package = ''
    modified_files = defaultdict(set)
    for line in process.stdout.decode('utf-8').splitlines():
        if match := re.fullmatch('Name *: (.*)', line):
            package = match.group(1)
        elif match := re.fullmatch(r'.*\s(.*) \[modified\]', line):
            modified_files[package].add(Path(match.group(1)).resolve())
    return modified_files


def get_untracked_files():
    # type: () -> list[Path]
    process = run([PACMAN, '-Qlq'], capture_output=True, check=True)
    tracked = set(process.stdout.decode('utf-8').splitlines())
    process = run(
        ['/usr/bin/find', '/etc', '-type', 'f'],
        capture_output=True,
        check=False, # `find` will "fail" on permission errors
    )
    existing = set(process.stdout.decode('utf-8').splitlines())
    return [Path(path) for path in (existing - tracked)]


def get_versioned_files():
    # type: () -> list[Path]
    result = []
    for path in Path(__file__).parent.glob('*/**'):
        path = path.resolve()
        if not path.is_file():
            continue
        if should_ignore(path):
            continue
        result.append(path)
    return result


def main():
    # type: () -> None
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        'action', nargs='?', choices=['update', 'discover'], default='discover',
        help='action to perform',
    )
    args = arg_parser.parse_args()
    if args.action == 'discover':
        paths = [
            *chain(*get_modified_files().values()),
            *get_untracked_files(),
        ]
        for path in sorted(paths):
            if not should_ignore(path):
                print(path)
    elif args.action == 'update':
        for repo_path in get_versioned_files():
            real_path = Path('/') / repo_path.relative_to(Path(__file__).parent)
            if not real_path.exists():
                continue # FIXME
            real_path.copy(repo_path)


if __name__ == '__main__':
    main()
