#!/usr/bin/env python3

import json
import re
from argparse import ArgumentParser
from collections import namedtuple
from datetime import datetime
from difflib import Differ
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
    assert data['_code'] == 'Ok', f'File contents request received code {data["_code"]}.'
    # convert the nodes to a dictionary
    return {node['id']: node for node in data['nodes']}


TreeLine = namedtuple('TreeLine', 'line_num, id, text, indent, sibling_index')


def dynalist_to_treelines(filename):
    nodes = get_file_nodes(filename)
    line_num = 1
    if 'children' not in nodes['root']:
        return
    for root_sibling_num, root_id in enumerate(nodes['root']['children'], start=1):
        stack = [(nodes[root_id], 0, root_sibling_num)]
        while stack:
            node, indent, sibling_index = stack.pop()
            node['content'] = re.sub(r'!\(([0-9]{4}-[0-9]{2}-[0-9]{2})\)', r'(\1)', node['content'])
            yield TreeLine(line_num, node['id'], node['content'], indent, sibling_index)
            line_num += 1
            if 'children' in node:
                stack.extend(
                    (nodes[child], indent + 1, child_sibling_num)
                    for child_sibling_num, child
                    in reversed(list(enumerate(node['children'])))
                )


def text_to_treelines(text):
    prv_indent = -1
    sibling_count = []
    for line_num, line in enumerate(text.splitlines()):
        indent = len(line) - len(line.lstrip())
        if indent < prv_indent:
            sibling_count = sibling_count[:indent + 1]
        elif indent == prv_indent + 1:
            sibling_count.append(-1)
        elif indent > prv_indent + 1:
            raise ValueError('invalid indentation')
        sibling_count[indent] += 1
        yield TreeLine(line_num, (line_num, 'line'), line.lstrip(), indent, sibling_count[indent])
        prv_indent = indent


def treelines_to_str(lines):
    return '\n'.join(
        line.indent * '\t' + line.text.rstrip()
        for line in lines if line.text.strip()
    )


def get_file(filename):
    return treelines_to_str(dynalist_to_treelines(filename))


def structure_diff(old_treelines, new_treelines, ignore_min=-1, ignore_max=-1):
    empty_treeline = TreeLine(*(None for _ in TreeLine._fields))
    old_index = 0
    new_index = 0
    while old_index < len(old_treelines) and new_index < len(new_treelines):
        old_treeline = old_treelines[old_index]
        new_treeline = new_treelines[new_index]
        if old_treeline.indent == new_treeline.indent:
            if ignore_min <= old_index < ignore_max and old_index < len(old_treelines):
                yield old_treeline, empty_treeline
                old_index += 1
            else:
                yield old_treeline, new_treeline
                old_index += 1
                new_index += 1
        elif old_treeline.indent < new_treeline.indent:
            yield empty_treeline, new_treeline
            new_index += 1
        elif old_treeline.indent > new_treeline.indent:
            yield old_treeline, empty_treeline
            old_index += 1
    while old_index < len(old_treelines):
        old_treeline = old_treelines[old_index]
        yield old_treeline, empty_treeline
        old_index += 1
    while new_index < len(new_treelines):
        new_treeline = new_treelines[new_index]
        yield empty_treeline, new_treeline
        new_index += 1


def treeline_diff(old_treelines, new_treelines):
    empty_treeline = TreeLine(*(None for _ in TreeLine._fields))
    old_lines = treelines_to_str(old_treelines).splitlines()
    new_lines = treelines_to_str(new_treelines).splitlines()
    old_index = 0
    new_index = 0
    section_start = []
    for line in Differ().compare(old_lines, new_lines):
        symbol = line[0]
        line = line[2:]
        old_treeline = old_treelines[old_index]
        new_treeline = new_treelines[new_index]
        if symbol == '?':
            continue
        elif symbol == ' ':
            if section_start:
                ignore_min = -1
                ignore_max = -1
                if section_start[0] < old_index:
                    first_lines = {}
                    last_lines = {}
                    for index in range(section_start[0], old_index):
                        treeline = old_treelines[index]
                        if treeline.indent not in first_lines:
                            first_lines[treeline.indent] = index
                        last_lines[treeline.indent] = index
                    delete_indent = min(first_lines.keys() & last_lines.keys())
                    ignore_min = first_lines[delete_indent]
                    ignore_max = last_lines[delete_indent]
                yield from structure_diff(
                    old_treelines[section_start[0]:old_index],
                    new_treelines[section_start[1]:new_index],
                    ignore_min - section_start[0],
                    ignore_max - section_start[0],
                )
                section_start = []
            yield old_treeline, new_treeline
            old_index += 1
            new_index += 1
        else:
            if not section_start:
                section_start = [old_index, new_index]
            if symbol == '-':
                old_index += 1
            elif symbol == '+':
                new_index += 1
        if not (old_index < len(old_treelines) and new_index < len(new_treelines)):
            break
    while old_index < len(old_treelines):
        old_treeline = old_treelines[old_index]
        yield old_treeline, empty_treeline
        old_index += 1
    while new_index < len(new_treelines):
        new_treeline = new_treelines[new_index]
        yield empty_treeline, new_treeline
        new_index += 1


def _sync_phase_1(file_id, old_treelines, new_treelines):
    parents = []
    id_map = {}
    changes = []
    ancestry = ['root']
    for old_treeline, new_treeline in treeline_diff(old_treelines, new_treelines):
        if new_treeline.id is None:
            #print('- ' + old_treeline.indent * 4 * ' ' + old_treeline.text)
            changes.append({
                'action': 'delete',
                'node_id': old_treeline.id,
            })
        elif old_treeline.id is None:
            #print('+ ' + new_treeline.indent * 4 * ' ' + new_treeline.text)
            parent_id = ancestry[new_treeline.indent]
            parent_id = id_map.get(parent_id, parent_id)
            parents.append((new_treeline, parent_id))
            changes.append({
                'action': 'insert',
                'parent_id': 'root',
                'content': new_treeline.text,
                'index': -1,
            })
        else:
            id_map[new_treeline.id] = old_treeline.id
            same = (
                old_treeline.indent == new_treeline.indent and
                old_treeline.text == new_treeline.text
            )
            if not same:
                changes.append({
                    'action': 'edit',
                    'node_id': old_treeline.id,
                    'content': new_treeline.text,
                })
        if new_treeline.id is not None:
            ancestry = ancestry[:new_treeline.indent + 1]
            ancestry.append(new_treeline.id)
    if changes:
        response = send_json_post(
            'https://dynalist.io/api/v1/doc/edit',
            {
                'token': TOKEN,
                'file_id': file_id,
                'changes': changes,
            },
        )
        assert response['_code'] == 'Ok', response
    return parents, id_map


def _sync_phase_2(file_id, old_treelines, parents, id_map):
    text_to_id = {treeline.text: treeline.id for treeline in old_treelines[-len(parents):]}
    changes = []
    for child_treeline, parent_id in parents:
        child_id = text_to_id[child_treeline.text]
        id_map[child_treeline.id] = child_id
        changes.append({
            'action': 'move',
            'node_id': child_id,
            'parent_id': id_map.get(parent_id, parent_id),
            'index': child_treeline.sibling_index,
        })
    if not changes:
        return
    response = send_json_post(
        'https://dynalist.io/api/v1/doc/edit',
        {
            'token': TOKEN,
            'file_id': file_id,
            'changes': changes,
        },
    )
    assert response['_code'] == 'Ok', response


def push(local, remote):
    file_id = get_file_id(remote)
    old_treelines = list(dynalist_to_treelines(remote))
    with local.open() as fd:
        time = datetime.now().isoformat(sep=' ', timespec='seconds')
        text = f'synced {time}\n' + fd.read()
    new_treelines = list(text_to_treelines(text))
    # find lines to modify in place
    parents, id_map = _sync_phase_1(file_id, old_treelines, new_treelines)
    old_treelines = list(dynalist_to_treelines(remote))
    # move new nodes into place
    _sync_phase_2(file_id, old_treelines, parents, id_map)


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('local', nargs='?', help='Local file to push.')
    arg_parser.add_argument('remote', help='Dynalist file to read from or write to.')
    args = arg_parser.parse_args()
    if args.local is None:
        print(treelines_to_str(dynalist_to_treelines(args.remote)))
    else:
        push(Path(args.local).expanduser().resolve(), args.remote)


if __name__ == '__main__':
    main()
