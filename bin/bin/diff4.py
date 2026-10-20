#!/usr/bin/env python3

from argparse import ArgumentParser
from os import environ
from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile


def determine_layout(lpath, bpath, rpath, opath):
    # type: (Path, Path, Path, Path) -> list[str]
    if bpath is not None:
        assert opath is None # not sure if this could be violated
        return 'all'
    if opath is None:
        assert bpath is None # not sure if this could be violated
        return 'diff'
    with lpath.open() as fd:
        ltext = fd.read()
    with rpath.open() as fd:
        rtext = fd.read()
    with opath.open() as fd:
        otext = fd.read()
    if ltext == otext:
        return 'output-right'
    elif rtext == otext:
        return 'output-left'
    else:
        return 'all'


def layout_diff_script(lpath, bpath, rpath, opath):
    # type: (Path, Path, Path, Path) -> list[str]
    """Create a script to show the left-right diff."""
    result = []
    # open the left file first
    result.append(f'tabnew {lpath}')
    # open the right file to the right of that
    result.append(f'rightbelow vertical diffsplit {rpath}')
    return result


def layout_left_script(lpath, bpath, rpath, opath):
    # type: (Path, Path, Path, Path) -> list[str]
    """Create a script to put the output on the left."""
    result = []
    # overwrite the output file with the left file
    lpath.copy(opath)
    # open the output file first
    result.append(f'tabnew {opath}')
    # open the right file to the right of that
    result.append(f'rightbelow vertical diffsplit {rpath}')
    return result


def layout_right_script(lpath, bpath, rpath, opath):
    # type: (Path, Path, Path, Path) -> list[str]
    """Create a script to put the output on the right."""
    result = []
    # overwrite the output file with the right file
    rpath.copy(opath)
    # open the left file first
    result.append(f'tabnew {lpath}')
    # open the output file to the right of that
    result.append(f'rightbelow vertical diffsplit {opath}')
    return result


def layout_all_script(lpath, bpath, rpath, opath):
    # type: (Path, Path, Path, Path) -> list[str]
    result = []
    # open the left file first
    result.append(f'tabnew {lpath}')
    # if there is a base, open it to the right
    if args.base:
        result.append(f'rightbelow vertical diffsplit {bpath}')
    # open the right file to the right of that
    result.append(f'rightbelow vertical diffsplit {rpath}')
    # if there is an output file, open it at the bottom
    if args.output:
        result.append(f'rightbelow diffsplit {opath}')
        result.append('execute "normal! \\<C-w>J"')
    return result


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    # set up the argument parser
    arg_parser = ArgumentParser()
    if 'NVIM' in environ:
        arg_parser.error('cowardly refusing to run in a nested neovim terminal')
    arg_parser.add_argument('left', type=Path, help='the left side of the diff/merge')
    arg_parser.add_argument('right', type=Path, help='the right side of the diff/merge')
    arg_parser.add_argument('--base', type=Path, help='the common ancestor file/directory')
    arg_parser.add_argument('--output', type=Path, help='the output file/directory')
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
    # determine layout
    layout = 'all'
    for version_paths in paths:
        new_layout = determine_layout(*version_paths)
        if layout == 'all':
            layout = new_layout
        elif layout != new_layout:
            layout = 'all'
            break
    # create a script to set up a tab for each file
    vimscript = []
    for version_paths in paths:
        if layout == 'diff':
            vimscript.extend(layout_diff_script(*version_paths))
        elif layout == 'output-left':
            vimscript.extend(layout_left_script(*version_paths))
        elif layout == 'output-right':
            vimscript.extend(layout_right_script(*version_paths))
        else:
            vimscript.extend(layout_all_script(*version_paths))
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
