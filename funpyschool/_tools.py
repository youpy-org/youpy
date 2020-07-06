# -*- encoding: utf-8 -*-
"""
"""


def as_ratio(obj):
    if isinstance(obj, int):
        return obj / 100
    elif isinstance(obj, float):
        return obj
    else:
        raise TypeError(f"expected (int, float), got {type(obj).__name__}")

def scale_size_by(size, ratio):
    return (round(size[0] * ratio), round(size[1] * ratio))
