#!/usr/bin/env python3

import json
from datetime import datetime
from argparse import ArgumentParser
from collections import namedtuple
from difflib import Differ
from os import environ
from os.path import expanduser

try:
    import requests
except ModuleNotFoundError as err:
    import sys # pylint: disable=ungrouped-imports,reimported
    from os import execv # pylint: disable=ungrouped-imports,reimported
    from os.path import exists, expanduser # pylint: disable=ungrouped-imports,reimported
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
    for root_sibling_num, root_id in enumerate(nodes['root']['children'], start=1):
        stack = [(nodes[root_id], 0, root_sibling_num)]
        while stack:
            node, indent, sibling_index = stack.pop()
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


def treelines_to_file(lines):
    return '\n'.join(line.indent * '\t' + line.text for line in lines)


def get_file(filename):
    return treelines_to_file(dynalist_to_treelines(filename))


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
                old_treeline = old_treelines[old_index]
            else:
                yield old_treeline, new_treeline
                old_index += 1
                new_index += 1
        elif old_treeline.indent < new_treeline.indent:
            yield empty_treeline, new_treeline
            new_index += 1
            new_treeline = new_treelines[new_index]
        elif old_treeline.indent > new_treeline.indent:
            yield old_treeline, empty_treeline
            old_index += 1
            old_treeline = old_treelines[old_index]
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
    old_lines = treelines_to_file(old_treelines).splitlines()
    new_lines = treelines_to_file(new_treelines).splitlines()
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


def sync(filename):
    file_id = get_file_id(filename)
    old_treelines = list(dynalist_to_treelines(filename))
    time = datetime.now().isoformat(sep=' ', timespec='seconds')
    with open(expanduser(f'~/journal/{filename}.journal')) as fd:
        text = f'synced {time}\n' + fd.read()
    new_treelines = list(text_to_treelines(text))
    # find lines to add and delete
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
                #print('% ' + new_treeline.indent * 4 * ' ' + new_treeline.text)
                changes.append({
                    'action': 'edit',
                    'node_id': old_treeline.id,
                    'content': new_treeline.text,
                })
            else: # FIXME can delete
                #print('  ' + old_treeline.indent * 4 * ' ' + old_treeline.text)
                pass
        if new_treeline.id is not None:
            ancestry = ancestry[:new_treeline.indent + 1]
            ancestry.append(new_treeline.id)
    # issue changes to Dynalist
    response = send_json_post(
        'https://dynalist.io/api/v1/doc/edit',
        {
            'token': TOKEN,
            'file_id': file_id,
            'changes': changes,
        },
    )
    assert response['_code'] == 'Ok', response
    old_treelines = list(dynalist_to_treelines(filename))
    text_to_id = {treeline.text: treeline.id for treeline in old_treelines[-len(parents):]}
    # move new nodes into place
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
    # issue changes to Dynalist
    response = send_json_post(
        'https://dynalist.io/api/v1/doc/edit',
        {
            'token': TOKEN,
            'file_id': file_id,
            'changes': changes,
        },
    )
    assert response['_code'] == 'Ok', response
    with open(expanduser(f'~/journal/{filename}.journal')) as fd:
        old_text = get_file(filename).strip()
        new_text = fd.read().strip()
        assert old_text == new_text, '\n'.join([
            *old_text.splitlines(),
            50 * '-',
            *new_text.splitlines(),
        ])


def main():
    arg_parser = ArgumentParser()
    arg_parser.set_defaults(action='pull')
    arg_parser.add_argument('--push', dest='action', action='store_const', const='push', help='Push file to Dynalist')
    arg_parser.add_argument('--filename', help='Dynalist filename. Defaults to "mobile"')
    args = arg_parser.parse_args()
    if not args.filename:
        if args.push:
            args.filename = 'notes'
        else:
            args.filename = 'mobile'
    if args.action == 'pull':
        print(treelines_to_file(dynalist_to_treelines(args.filename)))
    elif args.action == 'push':
        sync(args.filename)


if __name__ == '__main__':
    main()
