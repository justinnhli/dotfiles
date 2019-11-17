#!/usr/bin/env python3

import argparse
from json import loads as json_from_str
from datetime import datetime
from collections import OrderedDict, namedtuple
from pathlib import Path
from subprocess import run
from shutil import which


# registry


REGISTRY = OrderedDict()
Function = namedtuple('Function', 'name, function, do_all, hidden')


def register(do_all=True, hidden=False):

    def _register(func):
        name = func.__name__.replace('_', '-')
        REGISTRY[name] = Function(name, func, do_all, hidden)
        return func

    return _register


# main actions


@register(do_all=False)
def do_all():
    """Do all available actions."""
    for func in REGISTRY.values():
        if func.do_all:
            func.function()


# package manager actions


@register()
def update_arch():
    """Update Arch Linux packages."""
    if not which('pikaur'):
        return
    run(['pikaur', '-Syu'])


@register()
def update_brew():
    """Update Homebrew packages."""
    if not which('brew'):
        return
    run(['brew', 'update'], check=True)
    run(['brew', 'upgrade'], check=True)
    run(['brew', 'cask', 'upgrade'], check=True)
    run(['brew', 'cleanup'], check=True)


@register()
def update_cabal():
    """Update Cabal packages."""
    if not which('cabal'):
        return
    run_if_exists(['cabal', 'new-update'])


@register()
def update_pip(venv=None):
    """Update Python pip venv packages."""
    if venv is None:
        pip = Path(which('pip')).resolve()
    else:
        pip = Path(env['PYTHON_VENV_HOME']).joinpath(venv).resolve()
    if not pip.exists():
        return
    process = run(
        [pip, 'list', '--format', 'json'],
        check=True, capture_output=True,
    )
    packages = [
        package['name'] for package in
        json_from_str(process.stdout.decode('utf-8'))
    ]
    if packages:
        run(['pip', 'install', '--upgrade', *packages], check=True)


# file cleanup actions


@register(do_all=False)
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


@register(hidden=True)
def delete_dropbox_orphans():
    dropbox = Path('~/Dropbox').expanduser().resolve()
    if dropbox.exists():
        delete_orphans(dropbox)


@register(hidden=True)
def delete_desktop_orphans():
    desktop = Path('~/Desktop').expanduser().resolve()
    if desktop.exists():
        delete_orphans(desktop)


@register()
def delete_os_metadata():
    """Delete OS metadata files (Icon, .DS_Store, __MACOXS)."""
    print('deleting OS metadata files')
    for filename in ('Icon\r', '.DS_Store', '__MACOSX'):
        for filepath in Path().glob(f'**/{filename}'):
            filepath.unlink()
            print(f'    deleted {filepath}')


@register()
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


@register()
def find_conflicts():
    """Find conflicted Dropbox files."""
    print('finding conflicted Dropbox files')
    dropbox_path = Path('~/Dropbox').expanduser().resolve()
    for filepath in dropbox_path.glob('*conflicted*'):
        if '.dropbox.cache' not in str(filepath):
            print(filepath)


# CLI entry point


def generate_description():
    description = ['Available Actions:']
    callables = {k: v for k, v in REGISTRY.items() if not v.hidden}
    width = max(len(action) for action in callables.keys())
    format_str = f'{{: <{width}s}}'
    for action, function in callables.items():
        description.append(f'  {format_str.format(action)}  {function.function.__doc__}')
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
            REGISTRY[key].function()


if __name__ == '__main__':
    main()
