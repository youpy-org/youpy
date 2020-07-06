# -*- encoding: utf-8 -*-
"""
"""

import os
import re
from pathlib import Path

import pygame

from funpyschool._tools import as_ratio
from funpyschool._tools import scale_size_by


class Color:

    # Internally use pygame.Color to save space and get access to cool function
    # I don't want to recode myself.

    __slots__ = ("_c",)

    def __init__(self, red, green, blue, alpha=255):
        self._c = pygame.Color(red, green, blue)

    @property
    def red(self):
        return self._c.r

    @property
    def green(self):
        return self._c.g

    @property
    def blue(self):
        return self._c.b

Color.black  = Color(  0,   0,   0)
Color.white  = Color(255, 255, 255)
Color.gray   = Color(127, 127, 127)
Color.red    = Color(255,   0,   0)
Color.green  = Color(  0, 255,   0)
Color.blue   = Color(  0,   0, 255)
Color.yellow = Color(  0, 255, 255)
Color.purple = Color(255,   0, 255)

class Image:

    _NAME_RX = re.compile(r"(?P<index>\d+)?[- _]*(?P<name>\w+)\.\w+?")

    def __init__(self, path):
        self.path = Path(path)
        assert self.path.is_file()
        mo = self._NAME_RX.fullmatch(self.path.name)
        assert mo, f"invalid image file name '{path}'"
        self.name = mo.group("name")
        self.index = mo.group("index")
        self.index = 0 if self.index is None else int(self.index)
        self.surface = pygame.image.load(os.fspath(self.path))

    @property
    def rect(self):
        return self.surface.get_rect()

def scale_image_by(image, ratio=None):
    """
    Operate in place!
    """
    if ratio is None:
        return
    ratio = as_ratio(ratio)
    size = scale_size_by(image.rect.size, ratio)
    image.surface = pygame.transform.scale(image.surface, size)
