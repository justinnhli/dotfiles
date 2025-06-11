#!/usr/bin/env python3

import re
from subprocess import run as subprocess_run
from collections import defaultdict


def run(command):
    return subprocess_run(
        command,
        check=True,
        capture_output=True,
    ).stdout.decode('utf-8').splitlines()


def main():
    # collect subsets of packages
    casks = set(line.strip() for line in run(['brew', 'list', '--cask']))
    leaves = set(line.strip() for line in run(['brew', 'leaves']))
    explicit = set(line.strip() for line in run(['brew', 'leaves', '--installed-on-request']))
    explicit |= casks
    # collect and process dependency graph
    lines = [
        re.sub('[^ -~]', ' ', line.rstrip()) for line
        in run(['brew', 'deps', '--tree', '--installed'])
        if line.strip()
    ]
    packages = set()
    dependencies = defaultdict(set)
    stack = []
    for line in lines:
        indent = len(re.findall('    ', line))
        package = line.strip()
        packages.add(package)
        stack = stack[:indent]
        if stack:
            dependencies[stack[-1]].add(package)
        stack.append(package)
    # output as GraphViz
    print('digraph {')
    for package in sorted(packages):
        attrs = {}
        if package in casks:
            attrs['shape'] = 'box'
        if package in leaves:
            attrs['style'] = 'filled'
            attrs['fillcolor'] = '"#CC0000"'
        if package in explicit:
            attrs['style'] = 'filled'
            attrs['fillcolor'] = '"#73D216"'
        attrs_str = ''
        if attrs:
            attrs_str = '[' + ', '.join(f'{k}={v}' for k, v in sorted(attrs.items())) + ']'
        print(f'    "{package}" {attrs_str}')
    for parent, children in sorted(dependencies.items()):
        for child in children:
            print(f'    "{child}" -> "{parent}"')
    print('}')


if __name__ == '__main__':
    main()
