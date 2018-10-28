#!/usr/bin/env python3

import json
from argparse import ArgumentParser
from collections import namedtuple
from os import environ
from os.path import expanduser

try:
    import requests
except ModuleNotFoundError as err:
    import sys
    from os import execv
    from os.path import exists, expanduser
    VENV = 'ir'
    VENV_PYTHON = expanduser(f'~/.venv/{VENV}/bin/python3')
    if not exists(VENV_PYTHON):
        raise FileNotFoundError(' '.join([
            f'tried load module "{err.name}" with venv "{VENV}"',
            f'but could not find executable {VENV_PYTHON}',
        ]))
    execv(VENV_PYTHON, [VENV_PYTHON, *sys.argv])


TOKEN = environ['DYNALIST_TOKEN']


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


def get_file(filename):
    files = list_files()
    if filename not in files:
        raise KeyError(f'Cannot find file with title "{filename}"')
    data = send_json_post(
        'https://dynalist.io/api/v1/doc/read',
        {
            'token': TOKEN,
            'file_id': files[filename]['id'],
        },
    )
    assert data['_code'] == 'Ok', f'File contents request received code {data["_code"]}.'
    return data['nodes']


Node = namedtuple('Node', 'id content children')


def serialize_file(filename):

    def traverse(node, lines=None, depth=-1):
        if lines is None:
            lines = []
        if depth >= 0:
            lines.append(depth * '\t' + node.content)
        for child_id in node.children:
            traverse(cache[child_id], lines, depth + 1)
        return lines

    nodes = get_file(filename)
    cache = {}
    for node in nodes:
        if 'children' not in node:
            node['children'] = []
        cache[node['id']] = Node(*(node[attr] for attr in ['id', 'content', 'children']))
    return '\n'.join(traverse(cache['root']))


def diff(dynalist, filename):
    from difflib import Differ
    with open(expanduser(f'~/journal/{filename}.journal')) as fd:
        current = fd.read()
    print('\n'.join(Differ().compare(dynalist.splitlines(), current.splitlines())))


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('filename', nargs='?', default='mobile', help='Dynalist filename. Defaults to "mobile"')
    arg_parser.add_argument('--diff', action='store_true', help='Show diff instead of the file')
    args = arg_parser.parse_args()
    contents = serialize_file(args.filename)
    if args.filename == 'mobile' or not args.diff:
        print(contents)
    else:
        diff(contents, args.filename)


if __name__ == '__main__':
    main()
