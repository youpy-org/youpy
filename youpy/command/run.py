# -*- encoding: utf-8 -*-
"""Run a project.
"""


import argparse

from youpy.cli.argparse import ArgparseFormatter
from youpy.cli.argparse import parse_cli_args
from youpy.runner import run
from youpy.project import InvalidProjectDir
from youpy import logging


PROGNAME = "youpy-run"

def mkcli():
    def log_level(text):
        try:
            return logging.STR2LEVEL[text]
        except KeyError:
            raise argparse.ArgumentTypeError(
                "invalid log level '{}' (pick one in {})"
                .format(text, ", ".join(logging.STR2LEVEL.keys())))
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
    parser.add_argument(
        "--fps",
        action="store",
        type=int,
        default=30, # Scratch's FPS according to my experiment.
        help="Refresh rate of the simulation.")
    parser.add_argument(
        "--log-level",
        action="store",
        type=log_level,
        default="warning",
        help="Logging level for terminal")
    parser.add_argument(
        "--syslog-level",
        action="store",
        type=log_level,
        default="info",
        help="System logging level")
    parser.add_argument(
        "--log-context",
        action="store_true",
        default=False,
        help="Whether to prefix all log messages with the running context")
    return parser

def main(argv, opts):
    opts, _ = parse_cli_args(mkcli(), argv[1:], opts)
    try:
        run(opts.project_dir, show_fps=opts.show_fps, fps=opts.fps,
            log_level=opts.log_level, syslog_level=opts.syslog_level,
            log_context=opts.log_context)
        return 0
    except InvalidProjectDir as e:
        print(e)
        return 1
