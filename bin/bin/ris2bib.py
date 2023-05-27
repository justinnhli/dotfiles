#!/usr/bin/env python3
"""Convert ris bibliographical information to bibtex."""

# pylint: disable = line-too-long

import re
from argparse import ArgumentParser, FileType
from collections import defaultdict
from itertools import chain
from textwrap import dedent


PROP_MAP = {
    # author, editor, and pages are processed separately
    'title': ['TI', 'T1'],
    'year': ['PY', 'Y1'],
    'volume': ['VL'],
    'number': ['IS'],
    'url': ['UR'],
    'doi': ['DO'],
    'journal': ['JO'],
    'publisher': ['PB'],
}


def parse_ris(ris_str):
    # type: (str) -> dict[str, list[str]]
    """Parse the contents of a ris file."""
    ris = defaultdict(list)
    for line in ris_str.splitlines():
        if not re.fullmatch(r'\s*[A-Z0-9][A-Z0-9]\s*-.*', line):
            continue
        key, value = line.split('-', maxsplit=1)
        value = value.strip()
        if value:
            ris[key.strip()].append(value)
    return ris


def ris2bib(ris):
    # type: (dict[str, list[str]]) -> dict[str, str]
    """Convert ris file contents to bibtex."""
    bib = {}
    for bib_prop, ris_props in PROP_MAP.items():
        for ris_prop in ris_props:
            if ris_prop in ris:
                bib[bib_prop] = ris[ris_prop][0]
                break
    bib['author'] = ' and '.join(chain(*(
        ris[prop] for prop in ['AU', 'A1', 'A2', 'A3', 'A4']
    )))
    if 'ED' in ris:
        bib['editor'] = ' and '.join(ris['ED'])
    if 'SP' in ris and 'EP' in ris:
        bib['pages'] = ris['SP'][0] + '--' + ris['EP'][0]
    return bib


def bib_to_str(bib):
    # type: (dict[str, str]) -> str
    """Generate a bibtex entry from bibtex data."""
    bib_id = re.sub('[^0-9A-Za-z]', '', ''.join([
        bib['author'].split()[0].strip(','),
        bib['year'],
        *(word.title() for word in bib['title'].split()[:3]),
    ]))
    return '\n'.join([
        f'@article {{{bib_id},',
        *(
            f'    {key} = {{{value}}},'
            for key, value in sorted(bib.items())
        ),
        '}',
    ])


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    test()
    arg_parser = ArgumentParser()
    arg_parser.add_argument('fds', nargs='*', type=FileType('r'))
    args = arg_parser.parse_args()
    if args.fds == []:
        args = arg_parser.parse_args(['-'])
    for fd in args.fds:
        print(bib_to_str(ris2bib(parse_ris(fd.read().strip()))))


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
        '''
        @article {Garfinkel2022TeachingDynamicsTo,
            author = {Garfinkel, Alan and Bennoun, Steve and Deeds, Eric and Van Valkenburgh, Blaire},
            doi = {10.1007/s11538-022-00999-4},
            journal = {Bulletin of Mathematical Biology},
            number = {3},
            title = {Teaching Dynamics to Biology Undergraduates: the UCLA Experience},
            url = {https://doi.org/10.1007/s11538-022-00999-4},
            volume = {84},
            year = {2022},
        }
        ''',
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
        '''
        @article {Lerner2012SpreadingActivationIn,
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
        }
        ''',
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
        '''
        @article {Mandler1994HypermnesiaIncubationAnd,
            author = {Mandler, George},
            pages = {3--33},
            publisher = {The MIT Press},
            title = {Hypermnesia, incubation, and mind popping: On remembering without really trying.},
            year = {1994},
        }
        ''',
    ),
]


def test():
    # type: () -> None
    """Test the ris to bibtex conversion."""
    for ris_str, bib_str in TESTS:
        ris_str = dedent(ris_str).strip()
        bib_str = dedent(bib_str).strip()
        result = bib_to_str(ris2bib(parse_ris(ris_str))).strip()
        assert bib_str == result, '\n\n'.join([ris_str, bib_str, result])


if __name__ == '__main__':
    main()
