#!/usr/bin/env python3
"""Extract Kindle highlights and notes into Markdown.

Go to https://read.amazon.com/notebook and get the HTML source."""

import re
from argparse import ArgumentParser, FileType

from bs4 import BeautifulSoup


def _extract_text(soup):
    text = []
    for desc in soup.descendants:
        if not hasattr(desc, 'contents'):
            if desc.strip():
                text.append(desc.strip())
        elif str(desc) == '<br/>':
            text.append('<br>')
    return re.sub(r'  \+', ' ', ''.join(text).strip()).replace('<br>', '\n')


def extract_highlights(soup):
    metadata = soup.select('.kp-notebook-metadata')[0]
    location = re.search(
        r'Location:\s*([0-9, ]*)',
        _extract_text(metadata),
    )
    if not location:
        return None, None, None
    location = location.group(1).strip()
    highlight = soup.select('.kp-notebook-highlight')
    if highlight:
        highlight = _extract_text(highlight[0]).strip()
    else:
        highlight = None
    note = soup.select('.kp-notebook-note')
    if note:
        note = _extract_text(note[0])[len('Note:'):].strip()
    else:
        note = None
    return location, highlight, note


def _to_markdown_item(location, highlight, note):
    lines = [
        f'* > {highlight} - Location {location}',
    ]
    if note:
        lines.extend([
            f'    {note}',
        ])
    return '\n\n'.join(lines)


def highlights_to_markdown(html):
    items = []
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.select('.kp-notebook-row-separator'):
        location, highlight, note = extract_highlights(tag)
        if highlight or note:
            items.append(_to_markdown_item(location, highlight, note))
    print('\n\n'.join(items))


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        'filename',
        type=FileType('r'),
        help='The HTML source file',
    )
    args = arg_parser.parse_args()
    highlights_to_markdown(args.filename.read())


if __name__ == '__main__':
    main()
