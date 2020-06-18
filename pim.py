#!/usr/bin/env python3

from argparse import ArgumentParser

from journal import build_arg_parser as build_journal_arg_parser
from sheaf import build_arg_parser as build_sheaf_arg_parser

SECTIONS = ['journal', 'sheaf', 'archive', 'library']
SECTIONS = ['journal', 'sheaf',] # FIXME


def create_arg_parser():
    actions = ['lint']
    arg_parser = ArgumentParser()
    #arg_parser.add_argument('action', choices=(SECTIONS + actions))
    subparsers = arg_parser.add_subparsers()
    for section in SECTIONS:
        section_parser = subparsers.add_parser(section)
        parser_builder = globals()[f'build_{section}_arg_parser']
        parser_builder(section_parser)
    return arg_parser


def main():
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()
    args.function(arg_parser, args)


if __name__ == '__main__':
    main()
