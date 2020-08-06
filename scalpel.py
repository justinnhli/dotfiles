#!/usr/bin/env python3

import re
from os import utime
from collections import defaultdict
from pathlib import Path

from library import Library

SCALPEL_PATH = Path('~/pim/scalpel').expanduser().resolve()

LIBRARY = Library()


class Note:

    def __init__(self, path):
        self.path = path
        stat = path.stat()
        self.access_time = stat.st_atime_ns
        self.modified_time = stat.st_mtime_ns
        self.name = path.stem
        with self.path.open() as fd:
            self.text = fd.read()

    @property
    def references(self):
        return set(link[2:-2] for link in re.findall(r'\[\[[^]]*\]\]', self.text))

    @property
    def lines(self):
        return self.text.splitlines()

    @property
    def empty(self):
        return not any(
            line.strip() and not line.startswith('# ')
            for line in self.lines
        )

    @property
    def metadata(self):
        result = {}
        for line in self.lines:
            match = re.fullmatch('([a-z]+): *(.*)', line)
            if match:
                result[match.group(1)] = match.group(2)
            else:
                break
        return result



def read_notes():
    notes = {}
    backlinks = defaultdict(set)
    for path in SCALPEL_PATH.glob('**/*.md'):
        note = Note(path)
        if '#auto' in note.metadata.get('type', ''):
            note.path.unlink()
            continue
        if note.empty:
            note.path.unlink()
            continue
        for child in note.references:
            backlinks[child].add(note.name)
        notes[note.name] = note
    return notes, backlinks


def rewrite_note(note):
    # TODO: if it matches a Library paper, fill in bibliographical information
    lines = note.lines
    title_lines = [i for i, line in enumerate(lines) if line.startswith('# ')]
    if title_lines:
        lines[title_lines[0]] = f'# {note.name}'
    else:
        metadata_count = len(note.metadata)
        if metadata_count != 0:
            lines[metadata_count:metadata_count] = ''
            metadata_count += 1
        lines[metadata_count:metadata_count] = [
            f'# {note.name}',
            '',
        ]
    with note.path.open('w') as fd:
        fd.write('\n'.join(line.rstrip() for line in lines))
    utime(note.path, ns=(note.access_time, note.modified_time))


def write_stats_page(notes, backlinks):
    orphans = set()
    childless = set()
    for name, note in notes.items():
        if not backlinks[name]:
            orphans.add(name)
        if not note.references:
            childless.add(name)
    with (SCALPEL_PATH / 'Obsidian graph analysis.md').open('w') as fd:
        fd.write('\n'.join([
            'type: #auto',
            '',
            '# Obsidian graph analysis',
            '',
            '## Placeholder notes',
            '',
            *(f'* [[{name}]]' for name in sorted(set(backlinks).difference(notes))),
            '',
            '## Unlinked notes',
            '',
            *(f'* [[{name}]]' for name in sorted(orphans.intersection(childless))),
            '',
            '## Orphan notes',
            '',
            *(f'* [[{name}]]' for name in sorted(orphans)),
            '',
            '## Childless notes',
            '',
            *(f'* [[{name}]]' for name in sorted(childless)),
        ]))


def create_chronologies(notes):
    pass # TODO


def main():
    notes, backlinks = read_notes()
    for note in notes.values():
        rewrite_note(note)
    write_stats_page(notes, backlinks)


if __name__ == '__main__':
    main()
