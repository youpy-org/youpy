# -*- encoding: utf-8 -*-
"""Try to makes Python as fun as Scratch.
"""


import sys
import argparse

from youpy._command import import_command
from youpy._command import iter_command_names
from youpy._command import CommandNotFoundError
from youpy._cli.argparse import ArgparseFormatter
from youpy._cli.argparse import chop_cmdsep


PROGNAME = "youpy"

def mkcli():
    parser = argparse.ArgumentParser(
        prog=PROGNAME,
        description=__doc__,
        formatter_class=ArgparseFormatter,
        add_help=False)
    parser.add_argument(
        "--help",
        dest="_show_help",
        action="store_true",
        help="Print help")
    parser.add_argument(
        "subcommand",
        action="store",
        nargs="?",
        help="Name of the sub-command to run")
    return parser

def main(argv):
    cli = mkcli()
    options, rest = cli.parse_known_args(argv[1:])
    if options.subcommand is None:
        cli.print_help()
        print()
        print("sub-commands:")
        for i in iter_command_names():
            print("  ", i)
        return 1
    chop_cmdsep(rest)
    rest = [options.subcommand]+rest
    try:
        subcmd_mod = import_command(options.subcommand)
    except CommandNotFoundError as e:
        print(e)
        return 1
    return subcmd_mod.main(rest, options)

def sys_main():
    sys.exit(main(sys.argv))

if __name__ == "__main__":
    sys_main()
