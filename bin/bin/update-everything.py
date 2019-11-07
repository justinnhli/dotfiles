#!/usr/bin/env python3

import argparse
from datetime import datetime
from collections import OrderedDict
from pathlib import Path
from subprocess import run
from shutil import which

# utilities


def run_if_exists(command):
    if which(command[0]):
        run(command, check=True)


# registry

REGISTRY = OrderedDict()


def register(func):
    REGISTRY[func.__name__.replace('_', '-')] = func
    return func


# main actions


@register
def do_all():
    """Do all available actions."""
    for name, func in REGISTRY.items():
        if name != 'do-all':
            func()


# package manager actions


@register
def update_arch():
    """Update Arch Linux packages."""
    run_if_exists(['pikaur', '-Syu'])


@register
def update_brew():
    """Update Homebrew packages."""
    if not which('brew'):
        return
    run(['brew', 'update'], check=True)
    run(['brew', 'upgrade'], check=True)
    # FIXME deal with brew cask? unsure if its still necessary
    run(['brew', 'cleanup'], check=True)


@register
def update_cabal():
    """Update Cabal packages."""
    run_if_exists(['cabal', 'new-update'])


# file cleanup actions


@register
def delete_orphans(path=None):
    """Delete orphaned vim undo (.*.un~) files."""
    print('deleting orphaned vim undo files')
    if path is None:
        path = Path()
    timestamp = datetime.now().timestamp()
    threshold = 60 * 60 * 24 * 10 # 10 days
    for filepath in path.glob('**/.*.un~'):
        original = filepath.parent.joinpath(filepath.name[1:-4])
        should_delete = (
            (not original.exists())
            or (timestamp - filepath.stat().st_mtime > threshold)
        )
        if should_delete:
            filepath.unlink()
            print(f'    deleted {filepath}')


@register
def delete_os_metadata():
    """Delete OS metadata files (Icon, .DS_Store, __MACOXS)."""
    print('deleting OS metadata files')
    for filename in ('Icon\r', '.DS_Store', '__MACOSX'):
        for filepath in Path().glob(f'**/{filename}'):
            filepath.unlink()
            print(f'    deleted {filepath}')


@register
def merge_history():
    """Merge shell history logs."""
    print('merging shell history logs')
    history_path = Path('~/Dropbox/personal/logs').expanduser().resolve()
    years = set()
    for filepath in history_path.glob('*.shistory'):
        if not filepath.name.startswith('.'):
            years.add(filepath.name[:4])
    for year in sorted(years):
        filepaths = list(history_path.glob(f'{year}*.shistory'))
        if len(filepaths) == 1:
            continue
        shistory = set()
        for filepath in filepaths:
            shistory |= filepath.open().readlines()
            filepath.unlink()
        with Path(history_path).joinpath(f'{year}.shistory').open('w') as fd:
            for history in sorted(shistory):
                fd.write(history.strip())
                fd.write('\n')


@register
def find_conflicts():
    """Find conflicted Dropbox files."""
    print('finding conflicted Dropbox files')
    dropbox_path = Path('~/Dropbox').expanduser().resolve()
    for filepath in dropbox_path.glob('*conflicted*'):
        if '.dropbox.cache' not in str(filepath):
            print(filepath)


def generate_description():
    description = ['Available Actions:']
    width = max(len(action) for action in REGISTRY.keys())
    format_str = f'{{: <{width}s}}'
    for action, function in REGISTRY.items():
        description.append(f'  {format_str.format(action)}  {function.__doc__}')
    return '\n'.join(description)


def main():
    arg_parser = argparse.ArgumentParser(
        usage='%(prog)s [actions ...]',
        description=generate_description(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    arg_parser.add_argument(
        'actions', nargs='*',
        choices=sorted(REGISTRY.keys()), default='do-all',
        help=argparse.SUPPRESS
    )
    args = arg_parser.parse_args()
    if args.actions == 'do-all':
        do_all()
    else:
        for key in args.actions:
            REGISTRY[key]()


if __name__ == '__main__':
    main()
