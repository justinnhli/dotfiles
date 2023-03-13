#!/usr/bin/env python3
"""A script to update everything on a system."""

import argparse
from collections import OrderedDict, namedtuple
from datetime import datetime
from json import loads as json_from_str
from os import environ
from pathlib import Path
from shutil import which
from subprocess import run
from typing import Any, Callable


# registry


REGISTRY = OrderedDict()
Function = namedtuple('Function', 'name, function, hidden')


def register(hidden=False):
    # type: (bool) -> Callable[..., Any]
    """Register a function as a top-level action.

    Parameters:
        hidden (bool): Whether the function should be listed with --help.
            Defaults to False.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]:
            The function being registered.
    """

    def _register(func):
        # type: (Callable[..., Any]) -> Callable[..., Any]
        name = func.__name__.replace('_', '-')
        REGISTRY[name] = Function(name, func, hidden)
        return func

    return _register


# package manager actions


@register()
def update_arch():
    # type: () -> None
    """Update Arch Linux packages."""
    if not which('pikaur'):
        return
    run(['pikaur', '-Syu'], check=True)


@register()
def update_brew():
    # type: () -> None
    """Update Homebrew packages."""
    if not which('brew'):
        return
    run(['brew', 'update'], check=True)
    run(['brew', 'upgrade'], check=True)
    run(['brew', 'upgrade', '--cask'], check=True)
    run(['brew', 'autoremove'], check=True)
    run(['brew', 'cleanup'], check=True)


@register()
def update_cabal():
    # type: () -> None
    """Update Cabal packages."""
    if not which('cabal'):
        return
    run(['cabal', 'new-update'], check=True)


@register()
def update_vimplug():
    # type: () -> None
    """Update neovim packages."""
    if not which('nvim'):
        return
    run(['nvim', '-c', ':PlugUpgrade | PlugUpdate | qa'], check=True)


@register()
def update_pip(venv=None):
    # type: (str) -> None
    """Update Python pip venv packages.

    Parameters:
        venv (str): The name of the virtual environment to update
    """
    if venv is None:
        if not which('pip'):
            return
        pip = Path(which('pip')).resolve()
    else:
        pip = Path(environ['PYTHON_VENV_HOME']).joinpath(venv).resolve()
        if not pip.exists():
            return
    run(['pip', 'install', '--upgrade', 'pip'], check=False)
    process = run(
        [pip, 'list', '--format', 'json'],
        check=True, capture_output=True,
    )
    packages = [
        package['name'] for package in
        json_from_str(process.stdout.decode('utf-8'))
    ]
    if packages:
        env = environ.copy()
        env['PIP_REQUIRE_VIRTUALENV'] = 'false'
        run([pip, 'install', '--upgrade', *packages], env=env, check=True)


# file cleanup actions


@register()
def delete_orphans(path=None):
    # type: (Path) -> None
    """Delete orphaned vim undo (.*.un~) files.

    Parameters:
        path (Path): The directory to clear of orphans.
    """
    printed_header = False
    if path is None:
        path = Path.cwd()
    timestamp = datetime.now().timestamp()
    threshold = 60 * 60 * 24 * 14 # 14 days
    for filepath in path.glob('**/.*.un~'):
        original = filepath.parent.joinpath(filepath.name[1:-4])
        should_delete = (
            (not original.exists())
            or (timestamp - filepath.stat().st_mtime > threshold)
        )
        if should_delete:
            filepath.unlink()
            if not printed_header:
                print('deleting orphaned vim undo files')
                printed_header = True
            print(f'    deleted {filepath}')


@register()
def delete_os_metadata(path=None):
    # type: (Path) -> None
    """Delete OS metadata files (Icon, .DS_Store, __MACOSX).

    Parameters:
        path (Path): The directory to clear of OS metadata.
    """

    def rm_tree(path):
        if path.is_file():
            try:
                path.unlink()
            except PermissionError as err:
                print(err)
        else:
            for child in path.glob('*'):
                rm_tree(child)
            path.rmdir()

    if path is None:
        path = Path.cwd()
    print('deleting OS metadata files')
    for filename in ('Icon\r', '.DS_Store', '__MACOSX'):
        for filepath in path.glob(f'**/{filename}'):
            rm_tree(filepath)
            print(f'    deleted {filepath}')


@register()
def merge_history():
    # type: () -> None
    """Merge shell history logs."""
    print('merging shell history logs')
    history_path = Path('~/Dropbox/personal/logs').expanduser().resolve()
    years = set()
    for filepath in history_path.glob('*.shistory'):
        if not filepath.name.startswith('.'):
            years.add(filepath.name[:4])
    for year in sorted(years):
        shistory = set() # type: set[tuple[str, str, str]]
        for filepath in history_path.glob(f'{year}*.shistory'):
            with filepath.open() as fd:
                for line in fd:
                    components = line.strip().split('\t', maxsplit=3)
                    if len(components) != 4:
                        continue
                    date_str, host, pwd, command = components
                    # FIXME will need to deal with timezones in the future
                    if date_str.endswith('Z'):
                        pass
                    else:
                        pass
                    command = command.strip()
                    shistory.add((date_str, host, pwd, command))
            filepath.unlink()
        prev_line = ('', '', '')
        with history_path.joinpath(f'{year}.shistory').open('w', encoding='utf-8') as fd:
            for history in sorted(shistory):
                if history[1:] == prev_line:
                    continue
                fd.write('\t'.join(history))
                fd.write('\n')
                prev_line = history[1:]


@register()
def find_conflicts(path=None):
    # type: (Path) -> None
    """Find conflicted files.

    Parameters:
        path (Path): The directory to clear of OS metadata.
    """
    if path is None:
        path = Path.cwd()
    print('finding conflicted files')
    for conflict in path.glob('*conflicted*'):
        if '.dropbox.cache' not in str(conflict):
            print(conflict)


# personal update actions

@register()
def sync_library():
    # type: () -> None
    """Sync paper library."""
    library_path = Path('~/papers').expanduser().resolve()
    if not library_path.exists() or not which('library.py'):
        return
    run(['library.py', 'pull'], check=True)


@register()
def pull_git():
    # type: () -> None
    """Pull on all git repos."""
    git_path = Path('~/git').expanduser().resolve()
    if not git_path.exists():
        return
    run(['git-all', 'pull'], cwd=git_path, check=True)


@register()
def update_actr():
    # type: () -> None
    """Update the ACT-R subversion repository."""
    actr_path = Path('~/act-r').expanduser().resolve()
    if not actr_path.exists():
        return
    run(['git-all', 'pull'], cwd=actr_path, check=True)


# bundles


@register()
def update_everything():
    # type: () -> None
    """Perform general computer maintenance."""
    desktop_path = Path('~/Desktop').expanduser().resolve()
    dropbox_path = Path('~/Dropbox').expanduser().resolve()
    git_path = Path('~/git').expanduser().resolve()
    update_arch()
    update_brew()
    update_cabal()
    update_pip()
    for path in (desktop_path, dropbox_path, git_path):
        delete_orphans(path)
        delete_os_metadata(path)
        find_conflicts(path)
    merge_history()
    sync_library()
    update_vimplug()
    pull_git()
    update_actr()
    '''
    find . -type d -perm 777 | while read -r f; do
            chmod 755 "$f" && echo "	fixed permissions of $f"
    done
    '''


# CLI entry point


def generate_description():
    # type: () -> list[str]
    """Generate descriptions of command line arguments.

    Returns:
        list[str]: A list of arguments and their descriptions.
    """
    description = ['Available Actions:']
    callables = {k: v for k, v in REGISTRY.items() if not v.hidden}
    width = max(len(action) for action in callables.keys())
    format_str = f'{{: <{width}s}}'
    for action, function in callables.items():
        description.append(f'  {format_str.format(action)}  {function.function.__doc__.splitlines()[0]}')
    return description


def main():
    # type: () -> None
    """Deal with command line arguments."""
    arg_parser = argparse.ArgumentParser(
        usage='%(prog)s [actions ...]',
        description='\n'.join(generate_description()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    arg_parser.add_argument(
        'actions', nargs='*',
        choices=sorted(REGISTRY.keys()), default='update-everything',
        help=argparse.SUPPRESS
    )
    args = arg_parser.parse_args()
    if isinstance(args.actions, str):
        args.actions = [args.actions,]
    for key in args.actions:
        REGISTRY[key].function()


if __name__ == '__main__':
    main()
