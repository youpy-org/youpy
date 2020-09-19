# -*- encoding: utf-8 -*-
"""
"""


import sys
import os
from contextlib import contextmanager
import time


def as_ratio(obj):
    if isinstance(obj, int):
        return obj / 100
    elif isinstance(obj, float):
        return obj
    else:
        raise TypeError(f"expected (int, float), got {type(obj).__name__}")

def scale_size_by(size, ratio):
    return (round(size[0] * ratio), round(size[1] * ratio))

@contextmanager
def extended_sys_path(path):
    sys.path.append(os.path.abspath(path))
    try:
        yield
    finally:
        sys.path.pop()

IDENT_PATTERN = r"[^\s\d]\w+"

def rev_dict(d):
    return {v:k for k, v in d.items()}

class FrequencyMeter:

    def __init__(self):
        self._count = 0
        self._frequency = 0.0
        self._last_updated_at = 0.0
        self._updated = False

    def update(self):
        t = time.time()
        duration = (t - self._last_updated_at)
        if duration > 1.0: # sec
            self._frequency = self._count / duration
            self._count = 0
            self._last_updated_at = t
            self._updated = True
        else:
            self._count += 1
            self._updated = False
        return self._updated

    @property
    def frequency(self):
        return self._frequency

    @property
    def updated(self):
        return self._updated

    def __str__(self):
        return f"{self._frequency:.2f}"

    def __repr__(self):
        return f"{self.__class__.__name__}(count={self.count}, "\
            f"frequency={self._frequency}, "\
            f"last_updated_at={self._last_updated_at})"

def print_simple_banner(msg, separator="*", printer=print):
    banner_str = separator * len(msg)
    printer(banner_str)
    printer(msg)
    printer(banner_str)

def format_milliseconds(total_milliseconds):
    if not isinstance(total_milliseconds, int):
        raise TypeError("total_milliseconds must be int, not {}"
                        .format(type(total_milliseconds).__name__))
    total_seconds, milliseconds = divmod(total_milliseconds, 1000)
    total_minutes, seconds = divmod(total_seconds, 60)
    total_hours, minutes = divmod(total_minutes, 60)
    return f"{total_hours}:{minutes:02}:{seconds:02}.{milliseconds:03}"

def callback_name(cb):
    return ".".join((cb.__module__, cb.__qualname__))
