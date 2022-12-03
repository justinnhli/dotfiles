#!/usr/bin/env python3

import re
import sys
from collections import defaultdict
from textwrap import dedent
from itertools import chain


PROP_MAP = {
    # AU, ED, SP, EP is processed separately
    'TI': 'title',
    'T1': 'title',
    'PY': 'year',
    'Y1': 'year',
    'VL': 'volume',
    'IS': 'number',
    'UR': 'url',
    'DO': 'doi',
    'JO': 'journal',
    'PB': 'publisher',
}


def get_only(mapping, key, force_list=False):
    value = mapping[key]
    if force_list or len(value) != 1:
        return value
    else:
        return value[0]


def ris2bib(ris):
    ris_props = defaultdict(list)
    for line in ris.splitlines():
        if not re.fullmatch(r'\s*[A-Z0-9][A-Z0-9]\s*-.*', line):
            continue
        key, value = line.split('-', maxsplit=1)
        value = value.strip()
        if value:
            ris_props[key.strip()].append(value)
    bib_props = {}
    for ris_prop, bib_prop in PROP_MAP.items():
        if ris_prop in ris_props:
            if bib_prop not in bib_props:
                bib_props[bib_prop] = get_only(ris_props, ris_prop)
    bib_props['author'] = ' and '.join(chain(*(
        get_only(ris_props, prop, True)
        for prop in ['AU', 'A1', 'A2', 'A3', 'A4']
    )))
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
        for key, value in sorted(bib_props.items()):
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
    (
        '''
        TY  - JOUR
        T1  - Spreading Activation in an Attractor Network With Latching Dynamics: Automatic Semantic Priming Revisited
        AU  - Lerner, Itamar
        AU  - Bentin, Shlomo
        AU  - Shriki, Oren
        Y1  - 2012/11/01
        PY  - 2012
        DA  - 2012/11/01
        N1  - https://doi.org/10.1111/cogs.12007
        DO  - https://doi.org/10.1111/cogs.12007
        T2  - Cognitive Science
        JF  - Cognitive Science
        JO  - Cognitive Science
        SP  - 1339
        EP  - 1382
        VL  - 36
        IS  - 8
        KW  - Word recognition
        KW  - Semantic priming
        KW  - Neural networks
        KW  - Distributed representations
        KW  - Latching dynamics
        PB  - John Wiley & Sons, Ltd
        SN  - 0364-0213
        M3  - https://doi.org/10.1111/cogs.12007
        UR  - https://doi.org/10.1111/cogs.12007
        Y2  - 2022/10/05
        ER  - 
        ''',
        (
            'Lerner2012SpreadingActivationIn',
            '''
                author = {Lerner, Itamar and Bentin, Shlomo and Shriki, Oren},
                doi = {https://doi.org/10.1111/cogs.12007},
                journal = {Cognitive Science},
                number = {8},
                pages = {1339--1382},
                publisher = {John Wiley & Sons, Ltd},
                title = {Spreading Activation in an Attractor Network With Latching Dynamics: Automatic Semantic Priming Revisited},
                url = {https://doi.org/10.1111/cogs.12007},
                volume = {36},
                year = {2012},
            ''',
        ),
    ),
    (
        '''
        Provider: American Psychological Association
        Database: PsycINFO
        Content: application/x-research-info-systems

        TY  - CHAP
        DESCRIPTORS  - *Cognitive Processes;  *Forgetting;  *Memory; Recall (Learning)
        ID  - 1994-98352-001
        T1  - Hypermnesia, incubation, and mind popping: On remembering without really trying.
        T2  - Attention and performance 15:  Conscious and nonconscious information processing.
        T3  - Attention and performance series.
        A1  - Mandler, George
        SP  - 3
        EP  - 33
        Y1  - 1994
        CY  - Cambridge,  MA,  US
        PB  - The MIT Press
        SN  - 0-262-21012-6 (Hardcover)
        N2  - start with an overview and a critical analysis of . . . 3 areas [of implicit and explicit processes: hypermnesia, incubation, mind popping] / [consider] a theoretical analysis of the phenomena involved / the general thrust of these analyses will be informed by a framework that stresses activation and elaboration processes / the literature on hypermnesia and incubation is briefly reviewed, and the phenomena are placed in the context of activation/integration and elaboration processes  add . . . evidence [mind popping] that suggests that deliberate search for the target perception or memory may inhibit successful performance, whereas nonintentional attitudes favor such performance (PsycINFO Database Record (c) 2019 APA, all rights reserved)
        KW  - *Cognitive Processes
        KW  - *Forgetting
        KW  - *Memory
        KW  - Recall (Learning)
        ER  -
        ''',
        (
            'Mandler1994HypermnesiaIncubationAnd',
            '''
                author = {Mandler, George},
                pages = {3--33},
                publisher = {The MIT Press},
                title = {Hypermnesia, incubation, and mind popping: On remembering without really trying.},
                year = {1994},
            ''',
        ),
    ),
]


def test():
    for ris, (bib_id, bib_props) in TESTS:
        bib_id_a, bib_props_a = ris2bib(ris.strip())
        assert bib_id == bib_id_a
        for (key, value), expected in zip(sorted(bib_props_a.items()), dedent(bib_props).strip().splitlines()):
            actual = f'{key} = {{{value}}},'
            assert actual == expected, f"{actual}\n\ndoesn't match\n\n{expected}"


if __name__ == '__main__':
    main()
