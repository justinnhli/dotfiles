#!/usr/bin/env python3
"""A script that combines multiple Python linters and checkers."""

import re
import subprocess
import sys
from argparse import ArgumentParser
from collections import namedtuple
from os import environ
from pathlib import Path
from typing import List

VENV_PYTHON = Path(environ['PYTHON_VENV_HOME'], 'mypylint', 'bin', 'python3').expanduser()

Error = namedtuple('Error', 'filename, linenum, column, message')


def _module_exists(module):
    # type: (str) -> bool
    """Check if a module exists.

    Parameters:
        module (str): The module to check for.

    Returns:
        bool: True if the module exists in the venv, False otherwise.
    """
    try:
        subprocess.run([VENV_PYTHON, '-c', f'import {module}'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return False
    return True


def _err_print(message):
    # type: (str) -> None
    """Print to stderr.

    Parameters:
        message (str): The message to print.
    """
    print(message, file=sys.stderr)


def run_pylint(path):
    # type: (Path) -> List[Error]
    """Get errors from pylint.

    Parameters:
        path (Path): The path to the file to check.

    Returns:
        List[Error]: A list of errors.
    """
    process = subprocess.run(
        [
            str(VENV_PYTHON),
            '-m',
            'pylint',
            '--msg-template',
            '{path}:{line}:{column}: {msg} [{msg_id} {symbol}]',
            '--disable',
            'fixme',
            str(path),
        ],
        check=False,
        capture_output=True,
    )
    errors = []
    for line in process.stdout.decode('utf-8').splitlines():
        match = re.fullmatch(
            ' '.join([
                '(?P<filename>[^:]*):(?P<linenum>[0-9]+):(?P<column>-?[0-9]+):',
                r'(?P<message>.*) \[(?P<message_id>.*)\]',
            ]),
            line.strip(),
        )
        if not match:
            continue
        filename = str(Path(match.group('filename')).expanduser().resolve())
        linenum = match.group('linenum')
        column = match.group('column')
        message = match.group('message')
        message_id = match.group('message_id')
        errors.append(Error(
            filename,
            int(linenum),
            int(column),
            f'{message} (pylint {message_id})',
        ))
    return errors


def run_mypy(path):
    # type: (Path) -> List[Error]
    """Get errors from mypy.

    Parameters:
        path (Path): The path to the file to check.

    Returns:
        List[Error]: A list of errors.
    """
    process = subprocess.run(
        [
            VENV_PYTHON,
            '-m',
            'mypy',
            '--strict',
            '--follow-imports', 'error',
            '--ignore-missing-imports',
            '--no-warn-return-any',
            '--no-strict-optional',
            '--show-column-numbers',
            '--show-error-codes',
            str(path),
        ],
        check=False,
        capture_output=True,
    )
    errors = []
    for line in process.stdout.decode('utf-8').splitlines():
        match = re.fullmatch(
            ' '.join([
                '(?P<filename>[^:]*):(?P<linenum>[0-9]+):(?P<column>[0-9]+):',
                '(?P<output_type>[^:]*):',
                r'(?P<message>.*?) *\[(?P<message_id>[a-z-]*)\]',
            ]),
            line.strip(),
        )
        if not match:
            continue
        filename = str(Path(match.group('filename')).expanduser().resolve())
        linenum = match.group('linenum')
        column = match.group('column')
        output_type = match.group('output_type')
        message = match.group('message')
        message_id = match.group('message_id')
        if output_type != 'error':
            continue
        errors.append(Error(
            filename,
            int(linenum),
            int(column),
            f'{message} (mypy {message_id})',
        ))
    return errors


def run_pydocstyle(path):
    # type: (Path) -> List[Error]
    """Get errors from pydocstyle.

    Parameters:
        path (Path): The path to the file to check.

    Returns:
        List[Error]: A list of errors.
    """
    process = subprocess.run(
        [
            VENV_PYTHON,
            '-m',
            'pydocstyle',
            str(path),
        ],
        check=False,
        capture_output=True,
    )
    lines = process.stdout.decode('utf-8').splitlines()
    errors = []
    for line1, line2 in zip(lines[0::2], lines[1::2]):
        match1 = re.fullmatch('(?P<filename>[^:]*):(?P<linenum>[0-9]+) .*', line1.strip())
        match2 = re.fullmatch('^(?P<message_id>[^:]*): (?P<message>.*)', line2.strip())
        if match1 is None or match2 is None:
            continue
        filename = str(Path(match1.group('filename')).expanduser().resolve())
        linenum = match1.group('linenum')
        column = 0
        message = match2.group('message')
        message_id = match2.group('message_id')
        errors.append(Error(
            filename,
            int(linenum),
            int(column),
            f'{message} (pydocstyle {message_id})',
        ))
    return errors


def main():
    # type: () -> None
    """Deal with command line arguments."""
    has_pylint = _module_exists('pylint')
    if not has_pylint:
        _err_print('pylint not found, skipping')
    has_mypy = _module_exists('mypy')
    if not has_mypy:
        _err_print('mypy not found, skipping')
    has_pydocstyle = _module_exists('pydocstyle')
    if not has_pydocstyle:
        _err_print('pydocstyle not found, skipping')
    arg_parser = ArgumentParser()
    arg_parser.add_argument('--all', action='store_true', help='show all messages')
    arg_parser.add_argument('files', type=Path, nargs='+', help='files to lint')
    args = arg_parser.parse_args()
    has_errors = False
    for filepath in args.files:
        filepath = filepath.expanduser().resolve()
        errors = [] # type: list[Error]
        if has_pylint and (args.all or not errors):
            errors.extend(run_pylint(filepath))
        if has_mypy and (args.all or not errors):
            errors.extend(run_mypy(filepath))
        if has_pydocstyle and (args.all or not errors):
            errors.extend(run_pydocstyle(filepath))
        for error in sorted(errors):
            _err_print(f'{error.filename}:{error.linenum}:{error.column}: {error.message}')
        has_errors |= bool(errors)
    if has_errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
