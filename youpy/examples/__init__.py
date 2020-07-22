# -*- encoding: utf-8 -*-
"""Youpy's examples.
"""


import os

from youpy.runner import run as _run


_EXAMPLES_DIR = os.path.dirname(__file__)

def run_example(example_name):
    if not isinstance(example_name, str):
        raise TypeError("example_name must be str, not {}"
                        .format(type(example_name).__name__))
    example_path = os.path.join(_EXAMPLES_DIR, example_name)
    if not os.path.exists(example_path):
        raise ValueError(f"invalid example {example_name}")
    _run(example_path)
