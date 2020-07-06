# -*- encoding: utf-8 -*-
"""Extension to the standard argparse module.
"""


import argparse


class ArgparseFormatter(argparse.ArgumentDefaultsHelpFormatter,
                        argparse.RawDescriptionHelpFormatter):
    """Mix both formatter."""

def update_options(options, other):
    for k, v in vars(other).items():
        setattr(options, k, v)

def parse_cli_args(parser, argv, base_options=None, known=False):
    if known:
        options, rest = parser.parse_known_args(argv)
    else:
        options = parser.parse_args(argv)
        rest = []
    if base_options:
        update_options(options, base_options)
    chop_cmdsep(rest)
    return options, rest

def chop_cmdsep(args):
    if args and args[0].strip() == "--":
        args.pop(0)
