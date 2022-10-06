#!/usr/bin/env python3

import re
import sys
from collections import defaultdict
from textwrap import dedent


PROP_MAP = {
    # AU, ED, SP, EP is processed separately
    'TI': 'title',
    'T1': 'title',
    'PY': 'year',
    'VL': 'volume',
    'IS': 'number',
    'UR': 'url',
    'DO': 'doi',
    'JO': 'journal',
    'PB': 'publisher',
}


def get_only(mapping, key):
    value = mapping[key]
    if len(value) == 1:
        return value[0]
    else:
        return value


def ris2bib(ris):
    ris_props = defaultdict(list)
    for line in ris.splitlines():
        key, value = line.split('-', maxsplit=1)
        value = value.strip()
        if value:
            ris_props[key.strip()].append(value)
    bib_props = {}
    for ris_prop, bib_prop in PROP_MAP.items():
        if ris_prop in ris_props:
            assert bib_prop not in bib_props
            bib_props[bib_prop] = get_only(ris_props, ris_prop)
    bib_props['author'] = ' and '.join(get_only(ris_props, 'AU'))
    if 'ED' in ris_props:
        bib_props['editor'] = ' and '.join(get_only(ris_props, 'ED'))
    if 'SP' in ris_props and 'EP' in ris_props:
        bib_props['pages'] = get_only(ris_props, 'SP') + '--' + get_only(ris_props, 'EP')
    bib_id = re.sub('[^0-9A-Za-z]', '', ''.join([
        bib_props['author'].split()[0].strip(','),
        bib_props['year'],
        *(word.title() for word in bib_props['title'].split()[:3]),
    ]))
    return bib_id, bib_props


def main():
    test()
    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} RIS_FILE ...')
        sys.exit(1)
    for ris_file in sys.argv[1:]:
        with open(ris_file, encoding='utf-8') as fd:
            ris = fd.read().strip()
        bib_id, bib_props = ris2bib(ris)
        print(f'@article {{{bib_id},')
        for key, value in bib_props.items():
            print(f'    {key} = {{{value}}},')
        print(f'}}')


TESTS = [
    (
        '''
        TY  - JOUR
        AU  - Garfinkel, Alan
        AU  - Bennoun, Steve
        AU  - Deeds, Eric
        AU  - Van Valkenburgh, Blaire
        PY  - 2022
        DA  - 2022/02/12
        TI  - Teaching Dynamics to Biology Undergraduates: the UCLA Experience
        JO  - Bulletin of Mathematical Biology
        SP  - 43
        VL  - 84
        IS  - 3
        SN  - 1522-9602
        UR  - https://doi.org/10.1007/s11538-022-00999-4
        DO  - 10.1007/s11538-022-00999-4
        ID  - Garfinkel2022
        ER  -
        ''',
        (
            'Garfinkel2022TeachingDynamicsTo',
            '''
                author = {Garfinkel, Alan and Bennoun, Steve and Deeds, Eric and Van Valkenburgh, Blaire},
                doi = {10.1007/s11538-022-00999-4},
                journal = {Bulletin of Mathematical Biology},
                number = {3},
                title = {Teaching Dynamics to Biology Undergraduates: the UCLA Experience},
                url = {https://doi.org/10.1007/s11538-022-00999-4},
                volume = {84},
                year = {2022},
            ''',
        ),
    ),
]


def test():
    for ris, (bib_id, bib_props) in TESTS:
        bib_id_a, bib_props_a = ris2bib(ris.strip())
        assert bib_id == bib_id_a
        assert (
            dedent(bib_props).strip()
            == '\n'.join(f'{key} = {{{value}}},' for key, value in sorted(bib_props_a.items()))
        )


if __name__ == '__main__':
    main()
