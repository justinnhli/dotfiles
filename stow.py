#!/usr/bin/env python3

"""Manage stowed files."""

from argparse import ArgumentParser
from pathlib import Path
from subprocess import run as subprocess_run


def run(*terms):
    # type: (*str) -> str
    """Run a command line.

    Returns:
        str: The standard out.
    """
    return subprocess_run(
        terms,
        capture_output=True,
        check=True,
    ).stdout.decode('utf-8')


def install():
    # type: () -> None
    """Install package files."""
    home = Path('~').expanduser().resolve()
    for package in sorted(Path().resolve().glob('[a-z]*')):
        if not package.is_dir():
            continue
        run('stow', '--verbose', '--restow', '--target', str(home), package.name)


def check():
    # type: () -> bool
    """Check for stow errors.

    Returns:
        bool: True if there are errors, False otherwise.
    """
    tracked_files = run('git', 'ls-files', '--exclude-standard').splitlines()
    errors = False
    for tracked_file in sorted(tracked_files):
        path = Path(tracked_file)
        if len(path.parts) <= 1 or path.parts[0].startswith('.'):
            continue
        package = path.parts[0]
        stowlink_path = Path('~').expanduser().joinpath(*path.parts[1:])
        absolute_path = stowlink_path.resolve()
        relative_path = stowlink_path.relative_to(Path('~').expanduser())
        if not absolute_path.exists():
            print(f'[{package}] {relative_path} does not exist')
            errors = True
        elif absolute_path == stowlink_path:
            print(f'[{package}] {relative_path} is not linked')
            errors = True
    return bool(errors)


def main():
    # type: () -> None
    """Provide a CLI interface."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument('action', nargs='?', choices=['check', 'install'], default='check')
    args = arg_parser.parse_args()
    if args.action == 'check':
        check()
    elif args.action == 'install':
        install()


if __name__ == '__main__':
    main()
