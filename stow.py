#!/usr/bin/env python3

"""Manage stowed files."""

from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from subprocess import run as subprocess_run


def run(*terms):
    # type: (*str) -> str
    """Run a command line.

    Parameters:
        *terms (str): The terms of the command to run.

    Returns:
        str: The standard out.
    """
    return subprocess_run(
        terms,
        capture_output=True,
        check=True,
    ).stdout.decode('utf-8')


def install(*packages):
    # type: (*str) -> None
    """Install package files.

    Parameters:
        *packages (str): The packages to unstow.
    """
    stow_path = Path(__file__).resolve().parent
    if packages:
        package_paths = sorted(
            (stow_path / package) for package in packages
        )
        nonexistent = [path.name for path in package_paths if not path.is_dir()]
        if nonexistent:
            raise ValueError(f'nonexistent packages: {", ".join(nonexistent)}')
    else:
        package_paths = sorted(path for path in stow_path.glob('[a-z]*') if path.is_dir())
    home = str(Path('~').expanduser().resolve())
    for package_path in package_paths:
        run('stow', '--verbose', '--restow', '--target', home, package_path.name)


def check():
    # type: () -> None
    """Check for stow errors."""
    home = Path('~').expanduser()
    tracked_files = run('jj', 'file', 'list').splitlines()
    dir_used_by = defaultdict(set)
    errors = []
    for tracked_file in sorted(tracked_files):
        path = Path(tracked_file)
        if len(path.parts) <= 1 or path.parts[0].startswith('.'):
            continue
        package = path.parts[0]
        stowlink_path = home.joinpath(*path.parts[1:])
        absolute_path = stowlink_path.resolve()
        relative_path = stowlink_path.relative_to(Path('~').expanduser())
        if not absolute_path.exists():
            errors.append(f'[{package}] {relative_path} does not exist')
        elif absolute_path == stowlink_path:
            errors.append(f'[{package}] {relative_path} exists but is not a link')
        dir_used_by[stowlink_path.parent].add(package)
    for real_dir in sorted(dir_used_by):
        if len(dir_used_by[real_dir]) == 1 and real_dir == real_dir.resolve():
            errors.append(f'[{package}] {real_dir} exists but is not a link')
    for error in sorted(errors):
        print(error)


def main():
    # type: () -> None
    """Provide a CLI interface."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        'action', nargs='?', choices=['check', 'install'], default='check',
        help='action to perform',
    )
    arg_parser.add_argument('packages', nargs='*', help='packages to install')
    args = arg_parser.parse_args()
    if args.action == 'check':
        check()
    elif args.action == 'install':
        install(*args.packages)


if __name__ == '__main__':
    main()
