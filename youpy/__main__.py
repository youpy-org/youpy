# -*- encoding: utf-8 -*-
"""Try to makes Python as fun as Scratch.
"""


import sys
import argparse
import os

from youpy._command import import_command
from youpy._command import iter_command_names
from youpy._command import CommandNotFoundError
from youpy._cli.argparse import ArgparseFormatter
from youpy._cli.argparse import chop_cmdsep


PROGNAME = "youpy"

# Get replaced in the release process so that we do not probe the
# repository (which is not present) once released.
__version__ = 'dev'
__revision__ = 'git'

_VERSION_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                               "script", "version")

def get_version():
    if __version__ != 'dev':
        return __version__
    import subprocess as sp
    cmd = [_VERSION_SCRIPT, "get"]
    return sp.check_output(cmd).decode().strip()

def get_revision():
    if __revision__ != 'git':
        return __revision__
    import subprocess as sp
    cmd = [_VERSION_SCRIPT, "revision"]
    return sp.check_output(cmd).decode().strip()

def get_version_string():
    return \
        "youpy {v} "\
        "on python {pyv.major}.{pyv.minor}.{pyv.micro} "\
        "(rev: {rev})"\
        .format(v=get_version(),
                pyv=sys.version_info,
                rev=get_revision())

def mkcli():
    parser = argparse.ArgumentParser(
        prog=PROGNAME,
        description=__doc__,
        formatter_class=ArgparseFormatter,
        add_help=False)
    parser.add_argument(
        "--help",
        dest="show_help",
        action="store_true",
        help="Print help")
    parser.add_argument(
        "--version",
        dest="show_version",
        action="store_true",
        help="Print version number")
    parser.add_argument(
        "subcommand",
        action="store",
        nargs="?",
        help="Name of the sub-command to run")
    return parser

def main(argv):
    cli = mkcli()
    options, rest = cli.parse_known_args(argv[1:])
    if options.show_version:
        print(get_version_string())
        return 0
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
