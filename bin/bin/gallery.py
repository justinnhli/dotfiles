#!/usr/bin/env python3
"""Create a quick HTML gallery from images."""

from argparse import ArgumentParser
from datetime import datetime
from os import getcwd
from pathlib import Path


IMAGE_SUFFIXES = set(['jpg', 'jpeg', 'png', 'gif', 'tiff'])


def main():
    # type: () -> None
    """Provide an entry point for CLI."""
    # pylint: disable = superfluous-parens, unnecessary-lambda-assignment
    arg_parser = ArgumentParser()
    arg_parser.add_argument('--sort', choices=['name', 'modified', 'suffix'], default='name')
    arg_parser.add_argument('image_paths', type=Path, nargs='+')
    args = arg_parser.parse_args()
    if args.sort == 'name':
        key_fn = (lambda image_path: image_path.name)
    elif args.sort == 'modified':
        key_fn = (lambda image_path:
            datetime.fromtimestamp(image_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        )
    elif args.sort == 'suffix':
        key_fn = (lambda image_path: image_path.suffix)
    image_paths = [
        image_path for image_path in sorted(args.image_paths, key=key_fn)
        if image_path.suffix[1:].lower() in IMAGE_SUFFIXES
    ]
    print('<!DOCTYPE html>')
    print('<html lang="en">')
    print('<head>')
    print('<meta content="text/html; charset=utf-8" http-equiv="Content-Type">')
    print(f'<title>Gallery of {Path(getcwd()).resolve()}</title>')
    print('<style>')
    print('img {max-width:400px; max-height:400px;}')
    print('</style>')
    print('</head>')
    print('<body>')
    for image_path in image_paths:
        print(f'<a href="{image_path}"><img src="{image_path}" title="{image_path}"></a>')
    print('</body>')
    print('</html>')


if __name__ == '__main__':
    main()
