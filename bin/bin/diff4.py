#!/usr/bin/env python3

from argparse import ArgumentParser
from os import environ
from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile


def main():
    # set up the argument parser
    arg_parser = ArgumentParser()
    if 'NVIM' in environ:
        arg_parser.error('cowardly refusing to run in a nested neovim terminal')
    arg_parser.add_argument('left', type=Path, help='the left side of the diff/merge')
    arg_parser.add_argument('right', type=Path, help='the right side of the diff/merge')
    arg_parser.add_argument('--base', type=Path, help='the common ancestor file/directory')
    arg_parser.add_argument('--output', type=Path, help='the output file/directory')
    arg_parser.add_argument('--split', action='store_true', help='use a layout for splitting commits')
    # parse the arguments
    args = arg_parser.parse_args()
    # resolve all paths
    args.left = args.left.expanduser().resolve()
    args.right = args.right.expanduser().resolve()
    if args.base:
        args.base = args.base.expanduser().resolve()
    if args.output:
        args.output = args.output.expanduser().resolve()
    # validate arguments
    if args.split:
        args.base = args.output
        args.output = None
    roots = (args.left, args.base, args.right, args.output)
    arg_type = None
    for root in roots:
        if root is None:
            continue
        if not root.exists():
            arg_parser.error(f'argument {root} does not exist')
        root_arg_type = None
        if root.is_file():
            root_arg_type = 'file'
        elif root.is_dir():
            root_arg_type = 'dir'
        else:
            arg_parser.error(f'argument {root} is neither a file nor a directory')
        if arg_type is None:
            arg_type = root_arg_type
        elif arg_type != root_arg_type:
            arg_parser.error('arguments should either be all files or all directories')
    # build up the list of files to edit
    paths = []
    if arg_type == 'file':
        paths.append(
            (args.left, args.base, args.right, args.output),
        )
    else:
        relative_paths = set()
        for root in roots:
            if root is None:
                continue
            for dirpath, _, filenames in root.walk():
                relative_root = dirpath.relative_to(root)
                for filename in filenames:
                    relative_paths.add(relative_root / filename)
        for relative_path in sorted(relative_paths):
            paths.append(tuple(
                ((root / relative_path) if root else None)
                for root in roots
            ))
    # create a script to set up a tab for each file
    vimscript = []
    for lpath, bpath, rpath, opath in paths:
        # open the left file first
        vimscript.append(f'tabnew {lpath}')
        # if there is a base, open it to the right
        if args.base:
            vimscript.append(f'rightbelow vertical diffsplit {bpath}')
        # open the right file to the right of that
        vimscript.append(f'rightbelow vertical diffsplit {rpath}')
        # if there is an output file, open it at the bottom
        if args.output:
            vimscript.append(f'rightbelow diffsplit {opath}')
            vimscript.append('execute "normal! \\<C-w>J"')
    vimscript.append('tabclose 1')
    # write the vimscript to file
    vimscript_file = NamedTemporaryFile(mode='w', delete=False)
    with vimscript_file:
        vimscript.append(f'call delete("{vimscript_file.name}")')
        vimscript_file.write('\n'.join(vimscript))
    # run vim with the script
    print()
    print('\n'.join(vimscript))
    print()
    run(['nvim', '-S', vimscript_file.name], check=True)


if __name__ == '__main__':
    main()
