#!/usr/bin/env python3
"""A script to update everything on a system."""

import argparse
from collections import OrderedDict, namedtuple
from datetime import datetime
from json import loads as json_from_str
from os import environ
from pathlib import Path
from shutil import which
from subprocess import run, CalledProcessError
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
        return
    else:
        pip = Path(environ['PYTHON_VENV_HOME']).joinpath(venv).resolve()
        if not pip.exists():
            return
    run([str(pip), 'install', '--upgrade', 'pip'], check=False)
    process = run(
        [str(pip), 'list', '--format', 'json'],
        check=True, capture_output=True,
    )
    packages = [
        package['name'] for package in
        json_from_str(process.stdout.decode('utf-8'))
    ]
    if packages:
        env = environ.copy()
        env['PIP_REQUIRE_VIRTUALENV'] = 'false'
        run([str(pip), 'install', '--upgrade', *packages], env=env, check=True)


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
def delete_swap(path=None):
    # type: (Path) -> None
    """Delete old vim swap (.*.swp) files.

    Parameters:
        path (Path): The directory to clear of orphans.
    """
    printed_header = False
    if path is None:
        path = Path.cwd()
    timestamp = datetime.now().timestamp()
    threshold = 60 * 60 * 24 * 14 # 14 days
    for filepath in path.glob('**/.*.swp'):
        if timestamp - filepath.stat().st_mtime > threshold:
            filepath.unlink()
            if not printed_header:
                print('deleting old vim swap files')
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
        # type: (Path) -> None
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
def reset_permissions(path=None):
    # type: (Path) -> None
    """Reset directory permissions to 755.

    Parameters:
        path (Path): The root directory to reset permissions.
    """
    if path is None:
        path = Path.cwd()
    print('resetting directory permissions')
    for filepath in path.glob('**/*'):
        if not filepath.is_dir():
            continue
        if not filepath.exists():
            continue # if the file is a broken symlink
        if filepath.stat().st_mode == 0o40755:
            continue
        filepath.chmod(0o755)
        print(f'    changed permissions of {filepath}')


@register()
def reset_gnupg_permissions():
    # type: () -> None
    """Reset GnuPG settings directory permissions."""
    gnupg_path = Path('~/.gnupg').expanduser().resolve()
    run(
        [
            'chmod',
            '-R',
            'u=rw,u+X,go=',
            str(gnupg_path),
        ],
        check=True,
    )


@register()
def merge_history():
    # type: () -> None
    """Merge shell history logs."""
    print('merging shell history logs')
    history_path = Path('~/Dropbox/personal/logs/shistory/').expanduser().resolve()
    # collect all history
    shistory = set()
    years = set()
    for filepath in history_path.glob('*.shistory'):
        with filepath.open() as fd:
            for line in fd:
                components = line.strip().split('\t', maxsplit=3)
                if len(components) != 4:
                    continue
                date_str, host, pwd, command = components
                if date_str.endswith('Z'):
                    abs_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                else:
                    abs_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                    abs_date = (abs_date - abs_date.utcoffset()).replace(tzinfo=None)
                years.add(abs_date.year)
                command = command.strip()
                shistory.add((abs_date, date_str, host, pwd, command))
        filepath.unlink()
    # write out collated history
    for year in sorted(years):
        year_shistory = sorted(
            history for history in shistory
            if history[0].year == year
        )
        prev_line = ('', '', '', '')
        with history_path.joinpath(f'{year}.shistory').open('w', encoding='utf-8') as fd:
            for _, *history in year_shistory:
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
    for conflict in path.glob('**/*conflicted*'):
        if '.dropbox.cache' not in str(conflict):
            print(conflict)


# personal update actions

@register()
def update_package_lists():
    # type: () -> None
    """Update package lists in dotfiles repo."""

    def cmd_set(*commands):
        # type: (*str) -> set[str]
        return set(
            run(commands, check=True, capture_output=True)
            .stdout.decode('utf-8')
            .splitlines()
        )

    commands = {
        'brew': (lambda: cmd_set('brew', 'leaves') - cmd_set('brew', 'list', '--cask')),
        'brew-cask': (lambda: cmd_set('brew', 'list', '--cask')),
        'brew-tap': (lambda: cmd_set('brew', 'tap')),
        # FIXME 'npm': (lambda: set()),
        'pacman': (lambda:
            cmd_set('pacman', '--query', '--explicit', '--native', '--quiet')
            - cmd_set('pacman', '--query', '--groups', '--quiet', 'base-devel', 'texlive-most')
            - cmd_set('pacman', '--sync', '--list', '--quiet', 'core')
        ),
        'pikaur': (lambda: cmd_set('pacman', '--query', '--explicit', '--foreign', '--quiet')),
    } # type: dict[str, Callable[[], set[str]]]
    packages_dir = Path('~/.local/share/packages').expanduser().resolve()
    for filename, function in commands.items():
        packages = set()
        try:
            packages = function()
        except (FileNotFoundError, CalledProcessError):
            pass
        if packages:
            with (packages_dir / filename).open('w') as fd:
                fd.write('\n'.join(sorted(packages)))
                fd.write('\n')


@register()
def sync_library():
    # type: () -> None
    """Sync paper library."""
    library_path = Path('~/papers').expanduser().resolve()
    if not which('library.py'):
        return
    library_path.mkdir(exist_ok=True)
    run(['library.py', 'pull'], check=True)


@register()
def pull_git():
    # type: () -> None
    """Pull on all git repos."""
    git_path = Path('~/git').expanduser().resolve()
    if not git_path.exists():
        return
    run(['git-all.sh', 'pull'], cwd=git_path, check=True)


@register()
def update_actr():
    # type: () -> None
    """Update the ACT-R subversion repository."""
    actr_path = Path('~/act-r').expanduser().resolve()
    if not actr_path.exists():
        return
    run(['git-all.sh', 'pull'], cwd=actr_path, check=True)


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
    merge_history()
    for path in (desktop_path, dropbox_path, git_path):
        delete_orphans(path)
        delete_swap(path)
        delete_os_metadata(path)
        reset_permissions(path)
        find_conflicts(path)
    sync_library()
    update_vimplug()
    pull_git()
    update_actr()
    # this should happen after pull_git() due to the symbolic links
    reset_gnupg_permissions()


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
    for action, function in sorted(callables.items()):
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
