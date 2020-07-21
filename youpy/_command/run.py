# -*- encoding: utf-8 -*-
"""Run a project.
"""


import argparse

from youpy._cli.argparse import ArgparseFormatter
from youpy._cli.argparse import parse_cli_args
from youpy.runner import run
from youpy._project import InvalidProjectDir


PROGNAME = "youpy-run"

def mkcli():
    parser = argparse.ArgumentParser(
        prog=PROGNAME,
        description=__doc__,
        formatter_class=ArgparseFormatter)
    parser.add_argument(
        "project_dir",
        action="store",
        type=str,
        help="Path to the project directory to run")
    parser.add_argument(
        "--show-fps",
        action="store_true",
        help="Show FPS in the top-right corner of the screen.")
    return parser

def main(argv, opts):
    opts, _ = parse_cli_args(mkcli(), argv[1:], opts)
    try:
        run(opts.project_dir, show_fps=opts.show_fps)
        return 0
    except InvalidProjectDir as e:
        print(e)
        return 1
