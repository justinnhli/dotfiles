#!/usr/bin/env python3
"""Download a file from Dynalist."""

import json
import re
from argparse import ArgumentParser
from collections import namedtuple
from os import environ
from textwrap import indent
from typing import Any, Optional, Mapping

try:
    import requests
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

    run_with_venv('ir')


TOKEN = environ['DYNALIST_TOKEN']

TreeLine = namedtuple('TreeLine', 'id, text, indent, sibling_index')

def send_json_post(uri, data):
    # type: (str, Mapping[str, str]) -> dict[str, Any]
    """Send a post request with json data."""
    response = requests.post(uri, data=json.dumps(data))
    return json.loads(response.text)


def list_files():
    # type: () -> dict[str, dict[str, str]]
    """List all Dynalist files by name."""
    data = send_json_post(
        'https://dynalist.io/api/v1/file/list',
        {
            'token': TOKEN,
        },
    )
    assert data['_code'] == 'Ok', f'File listing request received code {data["_code"]}.'
    return {
        obj['title']: obj for obj in data['files']
        if obj['type'] == 'document'
    }


def get_file_id(filename, files=None):
    # type: (str, Optional[dict[str, dict[str, str]]]) -> str
    """Get the file ID of a Dynalist file."""
    if not files:
        files = list_files()
    if filename not in files:
        raise KeyError(f'Cannot find file with title "{filename}"')
    return files[filename]['id']


def get_file_nodes(filename, files=None):
    # type: (str, Optional[dict[str, dict[str, str]]]) -> dict[str, dict[str, Any]]
    """Get the nodes of a Dynalist file."""
    data = send_json_post(
        'https://dynalist.io/api/v1/doc/read',
        {
            'token': TOKEN,
            'file_id': get_file_id(filename, files),
        },
    )
    assert data['_code'] == 'Ok', f'File contents request failed with code {data["_code"]}.'
    # convert the nodes to a dictionary
    return {node['id']: node for node in data['nodes']}


def get_file(filename, files=None):
    # type: (str, Optional[dict[str, dict[str, str]]]) -> str
    """Get a file from Dynalist."""
    nodes = get_file_nodes(filename, files)
    assert 'children' in nodes['root']
    treelines = [] # type: list[TreeLine]
    for root_sibling_num, root_id in enumerate(nodes['root']['children'], start=1):
        stack = [(nodes[root_id], 0, root_sibling_num)] # type: list[tuple[dict[str, Any], int, int]]
        while stack:
            node, depth, sibling_index = stack.pop()
            node['content'] = re.sub(r'!\(([0-9]{4}-[0-9]{2}-[0-9]{2})\)', r'(\1)', node['content'])
            treelines.append(TreeLine(node['id'], node['content'], depth, sibling_index))
            if 'children' in node:
                stack.extend(
                    (nodes[child], depth + 1, child_sibling_num)
                    for child_sibling_num, child
                    in reversed(list(enumerate(node['children'])))
                )
    return '\n'.join(
        treeline.indent * '\t' + treeline.text.rstrip()
        for treeline in treelines if treeline.text.strip()
    )


def main():
    # type: () -> None
    """Provide an CLI entry point."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument('--list', action='store_true', help='list files instead of printing contents')
    arg_parser.add_argument('--headers', action='store_true', help='always include headers')
    arg_parser.add_argument('filenames', metavar='filename', nargs='*', help='Dynalist file(s) to read')
    args = arg_parser.parse_args()
    files = list_files()
    if args.list:
        print('\n'.join(sorted(files.keys())))
    else:
        if not args.filenames:
            args.filenames = list(files.keys())
        for filename in args.filenames:
            contents = get_file(filename, files)
            if args.headers or len(files) > 1:
                print(filename)
                print(indent(contents, '\t'))
            else:
                print(contents)


if __name__ == '__main__':
    main()
