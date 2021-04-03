#!/usr/bin/env python3

import sys
import re
from csv import DictReader
from pathlib import Path
from textwrap import indent


def to_markdown(path):
    with path.open() as fd:
        for row in DictReader(fd):
            for key, value in row.items():
                key = key.strip()
                value = re.sub(r'(http[\S]*)', r'<\1>', value)
                lines = [line.strip() for line in value.splitlines() if line.strip()]
                if len(lines) == 1:
                    print(f'* __{key}__: {value}')
                else:
                    print(f'* __{key}__')
                    print()
                    print(indent('\n\n'.join(line for line in lines), '    '))
                print()
            print('-----')
            print()


def main():
    to_markdown(Path(sys.argv[1]).expanduser().resolve())


if __name__ == '__main__':
    main()
