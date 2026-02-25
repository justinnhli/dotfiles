#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from subprocess import run


def main():
    # define arguments
    arg_parser = ArgumentParser()
    arg_parser.add_argument('inputs', nargs='+', type=Path)
    arg_parser.add_argument('-o', '--output', default='output.mp4', type=Path)
    arg_parser.add_argument('-f', '--force', action='store_true')
    arg_parser.add_argument('--dry-run', action='store_true')
    # parse arguments and check for errors
    args = arg_parser.parse_args()
    args.inputs = [path.expanduser().resolve() for path in args.inputs]
    for path in args.inputs:
        assert path.exists(), f'{path} does not exist'
    args.output = args.output.expanduser().resolve()
    assert args.force or not args.output.exists(), 'f{args.ouput} exists; pass --force to ignore'
    # build command
    command = ['ffmpeg']
    for path in args.inputs:
        command.extend(['-i', str(path)])
    command.extend(['-filter_complex', f'concat=n={len(args.inputs)}:v=1:a=1'])
    if args.force:
        command.append('-y')
    else:
        command.append('-n')
    command.append(str(args.output))
    # run command
    print(command)
    if not args.dry_run:
        run(command, check=True)


if __name__ == '__main__':
    main()
