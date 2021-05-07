#!/usr/bin/env python3

import sys
from collections import defaultdict


def main():

    def get_only(mapping, key):
        value = mapping[key]
        if len(value) == 0:
            return value[0]
        else:
            return value

    with open(sys.argv[1]) as fd:
        props = defaultdict(list)
        for line in fd.readlines():
            key, value = line.split('-', maxsplit=1)
            props[key.strip()].append(value.strip())
    bib_props = {}
    bib_props['title'] = get_only(props, 'TI')
    bib_props['author'] = ' and '.join(get_only(props, 'AU'))
    bib_props['year'] = get_only(props, 'PY')
    bib_props['volume'] = get_only(props, 'VL')
    bib_props['number'] = get_only(props, 'IS')
    bib_props['doi'] = get_only(props, 'DO')
    bib_props['pages'] = get_only(props, 'SP') + '--' + get_only(props, 'EP')
    bib_props['journal'] = get_only(props, 'JO')
    bib_id = ''.join([
        bib_props['author'].split()[0].strip(','),
        bib_props['year'],
        *(word.title() for word in bib_props['title'].split()[:3]),
    ])
    print(f'@article {{{bib_id},')
    for key, value in bib_props.items():
        print(f'    {key} = {{{value}}},')
    print(f'}}')


if __name__ == '__main__':
    main()
