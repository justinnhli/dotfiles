#!/usr/bin/env python3

"""Create a quick HTML gallery from images."""

from argparse import ArgumentParser
from pathlib import Path
from os import getcwd

IMAGE_SUFFIXES = set(['jpg', 'jpeg', 'png', 'gif', 'tiff'])

arg_parser = ArgumentParser()
arg_parser.add_argument('imagefiles', type=Path, nargs='+')
args = arg_parser.parse_args()

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
for imagefile in sorted(args.imagefiles):
    if imagefile.suffix[1:].lower() in IMAGE_SUFFIXES:
        print(f'<a href="{imagefile}"><img src="{imagefile}" title="{imagefile}"></a>')
print('</body>')
print('</html>')
