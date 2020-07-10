# -*- encoding: utf-8 -*-
"""
"""

import os
import re
from pathlib import Path

import pygame

from youpy._tools import as_ratio
from youpy._tools import scale_size_by


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

class Sprite:
    """Hold the data of a Sprite as used internally by the engine.

    We use the "native" coordinate system in this class (eg. top-left corner
    as used by pygame) for performance reason (it is rendered more often that
    it is modified).
    """

    def __init__(self, path, coordsys_name="center"):
        self._path = Path(path)
        assert self._path.is_dir()
        self.images = []
        self._index = -1
        self.visible = True
        self.rect = None
        self.coordsys_name = coordsys_name
        self._direction = 0

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._path.name

    def __repr__(self):
        return f"_engine.Sprite(name={self.name!r})"

    def go_to(self, x, y):
        if not isinstance(x, int):
            raise TypeError("x must be int, not {}"
                            .format(type(x).__name__))
        if not isinstance(y, int):
            raise TypeError("y must be int, not {}"
                            .format(type(y).__name__))
        setattr(self.rect, self.coordsys_name, (x, y))

    @property
    def current_image(self):
        return self.images[self._index]

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def point_in_direction(self, angle):
        if not isinstance(angle, int):
            raise TypeError("angle must be int, not {}"
                            .format(type(angle).__name__))
        if not -180 <= angle <= 180:
            raise ValueError("angle must be between -180 and 180 degree")
        self._direction = angle

    def direction(self):
        return self._direction

def scale_sprite_by(sprite, ratio=None):
    """
    Operate in place!
    """
    for image in sprite.images:
        scale_image_by(image, ratio=ratio)
    sprite.rect.size = sprite.current_image.rect.size
