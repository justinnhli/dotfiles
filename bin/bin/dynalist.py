#!/usr/bin/env python3

import json
import re
from argparse import ArgumentParser
from collections import namedtuple
from os import environ

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
    response = requests.post(uri, data=json.dumps(data))
    return json.loads(response.text)


def list_files():
    data = send_json_post(
        'https://dynalist.io/api/v1/file/list',
        {
            'token': TOKEN,
        },
    )
    assert data['_code'] == 'Ok', f'File listing request received code {data["_code"]}.'
    return {obj['title']: obj for obj in data['files']}


def get_file_id(filename):
    files = list_files()
    if filename not in files:
        raise KeyError(f'Cannot find file with title "{filename}"')
    return files[filename]['id']


def get_file_nodes(filename):
    data = send_json_post(
        'https://dynalist.io/api/v1/doc/read',
        {
            'token': TOKEN,
            'file_id': get_file_id(filename),
        },
    )
    assert data['_code'] == 'Ok', f'File contents request failed with code {data["_code"]}.'
    # convert the nodes to a dictionary
    return {node['id']: node for node in data['nodes']}


def get_file(filename):
    nodes = get_file_nodes(filename)
    assert 'children' not in nodes['root']
    treelines = [] # type: list[TreeLine]
    for root_sibling_num, root_id in enumerate(nodes['root']['children'], start=1):
        stack = [(nodes[root_id], 0, root_sibling_num)]
        while stack:
            node, indent, sibling_index = stack.pop()
            node['content'] = re.sub(r'!\(([0-9]{4}-[0-9]{2}-[0-9]{2})\)', r'(\1)', node['content'])
            treelines.append(TreeLine(node['id'], node['content'], indent, sibling_index))
            if 'children' in node:
                stack.extend(
                    (nodes[child], indent + 1, child_sibling_num)
                    for child_sibling_num, child
                    in reversed(list(enumerate(node['children'])))
                )
    return '\n'.join(
        treeline.indent * '\t' + treeline.text.rstrip()
        for treeline in treelines if treeline.text.strip()
    )


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('remote', help='Dynalist file to read from or write to.')
    args = arg_parser.parse_args()
    print(get_file(args.remote))


if __name__ == '__main__':
    main()
