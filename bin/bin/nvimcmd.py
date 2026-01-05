#!/usr/bin/env python3
"""Command neovim from the built-in terminal."""

import re
import sys
from os import environ
from os.path import expanduser, realpath

try:
    from pynvim import attach
    from pynvim.api.nvim import NvimError
except (ModuleNotFoundError, ImportError) as err:

    def run_with_venv(venv):
        # type: (str) -> None
        """Run this script in a virtual environment.

        Parameters:
            venv (str): The virtual environment to use.

        Raises:
            FileNotFoundError: If the virtual environment does not exist.
            ImportError: If the virtual environment does not contain the necessary packages.
        """
        # pylint: disable = ungrouped-imports, reimported, redefined-outer-name, import-outside-toplevel
        import sys
        from os import environ, execv
        from pathlib import Path
        venv_python = Path(environ['PYTHON_VENV_HOME'], venv, 'bin', 'python3').expanduser()
        if not venv_python.exists():
            raise FileNotFoundError(f'could not find venv "{venv}" at executable {venv_python}')
        if sys.executable == str(venv_python):
            raise ImportError(f'no module {err.name} in venv "{venv}" ({venv_python})')
        execv(str(venv_python), [str(venv_python), *sys.argv])

    run_with_venv('pynvim')


EDIT_COMMANDS = {
    'tabnew': True,
    'e': False,
    'edit': False,
    'sp': True,
    'vsp': True,
    'split': True,
    'vsplit': True,
}


def print_and_exit(message):
    # type: (str) -> None
    """Print and exit with error code 1."""
    print(sys.argv[0] + ': ' + message)
    sys.exit(1)


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    if len(sys.argv) == 1:
        print_and_exit(f'Usage: {sys.argv[0]} <command> [arguments]')
    addr = environ.get('NVIM', None)
    if not addr:
        print_and_exit('$NVIM not set; quitting')
    nvim = attach('socket', path=addr)
    commands = []
    command = sys.argv[1]
    args = sys.argv[2:]
    if command in EDIT_COMMANDS:
        args = [realpath(expanduser(arg)).replace(' ', r'\ ') for arg in args]
        args = [re.sub(r'([^\\])\%', r'\1\%', arg) for arg in args]
        if EDIT_COMMANDS[command]:
            for arg in args:
                commands.append(' '.join([command, arg]))
    if not commands:
        commands.append(' '.join([command,] + args))
    try:
        for command in commands:
            nvim.command(command)
    except NvimError as nve:
        if hasattr(nve.args[0], 'decode'):
            print_and_exit(nve.args[0].decode('utf-8'))
        else:
            print_and_exit(nve.args[0])


if __name__ == '__main__':
    main()
