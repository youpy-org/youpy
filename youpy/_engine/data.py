# -*- encoding: utf-8 -*-
"""
"""

import os
import re
from pathlib import Path
from collections import OrderedDict

import pygame

from youpy._tools import as_ratio
from youpy._tools import scale_size_by
from youpy import math
from youpy import math


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

    class _State:

        __slots__ = ("visible", "rect", "coordsys_name", "_direction")

        def __init__(self, coordsys_name="center"):
            self.visible = True
            self.rect = None
            self.coordsys_name = coordsys_name
            self._direction = 0 # direction angle in degree

        def go_to(self, x, y):
            p = self.position()
            if x is None:
                x = p[0]
            if y is None:
                y = p[1]
            setattr(self.rect, self.coordsys_name, (x, y))

        def position(self):
            return getattr(self.rect, self.coordsys_name)

        def direction(self):
            return self._direction

        def turn_counter_clockwise(self, angle):
            self._direction += angle
            self._direction %= 360

        def copy(self):
            n = type(self)(coordsys_name=self.coordsys_name)
            n.visible = self.visible
            n.rect = self.rect.copy()
            n._direction = self._direction
            return n

    def __init__(self, path, coordsys_name="center"):
        self._path = Path(path)
        assert self._path.is_dir()
        self.images = []
        self._index = -1
        self._st = self._State(coordsys_name=coordsys_name)

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._path.name

    def __repr__(self):
        return f"_engine.Sprite(name={self.name!r})"

    @property
    def rect(self):
        return self._st.rect

    @rect.setter
    def rect(self, new_rect):
        self._st.rect = new_rect

    def go_to(self, x, y):
        self._st.go_to(x, y)

    def position(self):
        return self._st.position()

    @property
    def current_image(self):
        return self.images[self._index]

    def show(self):
        self._st.visible = True

    def hide(self):
        self._st.visible = False

    @property
    def visible(self):
        return self._st.visible

    @visible.setter
    def visible(self, visible):
        self._st.visible = visible

    def point_in_direction(self, angle):
        if not isinstance(angle, int):
            raise TypeError("angle must be int, not {}"
                            .format(type(angle).__name__))
        if not 0 <= angle < 360:
            raise ValueError(
                "angle must be between 0 and 360 degree excluded, "\
                f"but is equal to {angle}")
        self._st._direction = angle

    def direction(self):
        return self._st.direction()

    def turn_counter_clockwise(self, angle):
        if not isinstance(angle, int):
            raise TypeError("angle must be int, not {}"
                            .format(type(angle).__name__))
        if not 0 <= angle < 360:
            raise ValueError(
                "angle must be between 0 and 360 degree excluded, "\
                f"but is equal to {angle}")
        return self._st.turn_counter_clockwise(angle)

    def move(self, step):
        if not isinstance(step, int):
            raise TypeError("step must be int, not {}"
                            .format(type(step).__name__))
        # print(f"move direction={self._direction}, step={step}, {x=}, {y=}, dx={dx}, dy={dy}")
        self.move_by(step * math.fast_cos(self._st._direction),
                     -step * math.fast_sin(self._st._direction))

    def move_by(self, step_x, step_y):
        x, y = self.position()
        self.go_to(x + step_x, y + step_y)

    def get_state(self):
        return self._st.copy()

def scale_sprite_by(sprite, ratio=None):
    """
    Operate in place!
    """
    for image in sprite.images:
        scale_image_by(image, ratio=ratio)
    sprite.rect.size = sprite.current_image.rect.size

class _Scene:
    """Internal scene representation."""

    def __init__(self):
        self.width = 480
        self.height = 360
        self.surface = None
        self.backdrops = OrderedDict() # important to support "next backdrop"
        self._backdrop = None

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def rect(self):
        return pygame.Rect(0, 0, self.width, self.height)

    @property
    def center(self):
        return (self.width // 2, self.height // 2)

    @property
    def topleft(self):
        return (0, 0)

    @property
    def backdrop(self):
        return self._backdrop

    @backdrop.setter
    def backdrop(self, backdrop):
        self._backdrop = self.backdrops[backdrop]

class Scene:
    """Scene front-end.

    Concurrently accessed from user script. Passed to every running script.
    Should be pickable.
    """

    @classmethod
    def from_scene(cls, scene):
        return cls(width=scene.width,
                   height=scene.height,
                   coordsys=scene.coordsys,
                   anglesys=scene.anglesys)

    def __init__(self, width=None, height=None, coordsys=None, anglesys=None):
        self._width = width
        self._height = height
        self._coordsys = coordsys
        self._anglesys = anglesys

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

# Sentinel object to mark scene edge in collision list.
SCENE_EDGE = object()
