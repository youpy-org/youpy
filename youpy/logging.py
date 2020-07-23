# -*- encoding: utf-8 -*-
"""
"""


import logging
import sys

from youpy.tools import rev_dict


LEVEL2STR = {
    logging.DEBUG: "debug",
    logging.INFO: "info",
    logging.WARNING: "warning",
    logging.ERROR: "error",
    logging.FATAL: "fatal",
}
STR2LEVEL = rev_dict(LEVEL2STR)

def init_logger(project, log_level=None):
    log_level = log_level or logging.INFO

    youpy_logger = logging.getLogger("youpy")
    youpy_logger.setLevel(log_level)

    precise_formatter = logging.Formatter(
        "%(asctime)s: %(name)s: %(lowerlevelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    brief_formatter = logging.Formatter(
        "%(name)s: %(lowerlevelname)s: %(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(project.log_file,
                                       mode="w", encoding="utf-8")

    stream_handler.setFormatter(brief_formatter)
    stream_handler.setLevel(log_level)
    file_handler.setFormatter(precise_formatter)
    # file_handler.setLevel(logging.DEBUG)

    youpy_logger.addHandler(stream_handler)
    youpy_logger.addHandler(file_handler)

    return youpy_logger

_old_record_factory = logging.getLogRecordFactory()

def record_factory(*args, **kwargs):
    record = _old_record_factory(*args, **kwargs)
    record.lowerlevelname = record.levelname.lower()
    return record

logging.setLogRecordFactory(record_factory)

def get_client_logger_name(name):
    return f"youpy.client.{name}"
