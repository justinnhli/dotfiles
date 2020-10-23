"""Utility functions for PIM."""

import re
import sys
from os import environ, execv
from pathlib import Path

DATE_REGEX = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')


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


def titlize(*parts):
    # type: (*str) -> str
    """Convert strings into a title."""
    return re.sub(' +', ' ', ' '.join(parts)).title()


def filenamize(*parts):
    # type: (*str) -> str
    """Convert strings into a valid filename slug."""
    title = re.sub('[^-0-9a-z ]', '', ' '.join(parts).lower())
    title = re.sub(' +', ' ', title).title()
    return title.lower().replace(' ', '-')
