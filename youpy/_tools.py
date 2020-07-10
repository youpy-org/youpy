# -*- encoding: utf-8 -*-
"""
"""


import sys
import os
from contextlib import contextmanager
import math


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

def degree_to_radian(degree):
    return degree * math.pi / 180

def radian_to_degree(radian):
    return radian * 180 / math.pi
