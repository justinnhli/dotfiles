#!/usr/bin/env python3
"""Test colors in a terminal."""

# modified from https://askubuntu.com/a/27318

import sys

write = sys.stdout.write
for i in range(2):
    for j in range(30, 38):
        for k in range(40, 48):
            write(f'\33[{i:d};{j:d};{k:d}m{i:d};{j:d};{k:d}\33[m ')
        write('\n')
