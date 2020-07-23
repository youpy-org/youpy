# -*- encoding: utf-8 -*-
"""
"""


import logging
import sys

from youpy.tools import rev_dict

from logging import DEBUG
from logging import INFO
from logging import WARNING
from logging import ERROR
from logging import FATAL
PRINT = FATAL + 1000
logging.addLevelName(PRINT, "PRINT")

LEVEL2STR = {
    DEBUG: "debug",
    INFO: "info",
    WARNING: "warning",
    ERROR: "error",
    FATAL: "fatal",
}
STR2LEVEL = rev_dict(LEVEL2STR)

ROOT_LOGGER_NAME = "youpy"

def as_log_level(obj):
    if isinstance(obj, str):
        return STR2LEVEL[obj.lower()]
    elif isinstance(obj, int):
        return obj
    else:
        raise TypeError(f"cannot interpret object of type {type(obj).__name__} to as a log level")

def init_logger(project, log_level=None, syslog_level=None):
    if log_level is None:
        log_level = logging.INFO
    if syslog_level is None:
        syslog_level = logging.INFO
    log_level = as_log_level(log_level)
    syslog_level = as_log_level(syslog_level)

    youpy_logger = logging.getLogger(ROOT_LOGGER_NAME)
    # Pass all messages to handlers. Severity-level are configured by
    # handlers.
    youpy_logger.setLevel(-1)

    precise_formatter = logging.Formatter(
        "%(asctime)s: %(name)s: %(lowerlevelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    brief_formatter = logging.Formatter(
        "%(name)s: %(lowerlevelname)s: %(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    system_file_handler = logging.FileHandler(project.syslog_file,
                                              mode="w", encoding="utf-8")
    user_file_handler = logging.FileHandler(project.user_log_file,
                                            mode="w", encoding="utf-8")

    stream_handler.setFormatter(brief_formatter)
    stream_handler.setLevel(log_level)

    system_file_handler.setFormatter(precise_formatter)
    system_file_handler.setLevel(syslog_level)

    user_file_handler.setFormatter(precise_formatter)
    user_file_handler.setLevel(log_level)
    user_file_handler.addFilter(UserLogFilter())

    youpy_logger.addHandler(stream_handler)
    youpy_logger.addHandler(system_file_handler)
    youpy_logger.addHandler(user_file_handler)

    return youpy_logger

_old_record_factory = logging.getLogRecordFactory()

def record_factory(*args, **kwargs):
    record = _old_record_factory(*args, **kwargs)
    record.lowerlevelname = record.levelname.lower()
    return record

logging.setLogRecordFactory(record_factory)

USER_LOGGER_NAME = f"{ROOT_LOGGER_NAME}.user"

def get_user_logger_name(name):
    return f"{USER_LOGGER_NAME}.{name}"


class UserLogFilter(logging.Filter):

    def filter(self, record):
        return record.name.startswith(USER_LOGGER_NAME)

def getLogger(name):
    return logging.getLogger(name)
