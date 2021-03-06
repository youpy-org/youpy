# -*- encoding: utf-8 -*-
"""
"""

import os
import re
from pathlib import Path
from collections import OrderedDict

import pygame

from youpy.tools import as_ratio
from youpy.tools import scale_size_by
from youpy import math
from youpy.math import Point
from youpy.concurrency import ReadLock
from youpy.concurrency import WriteLock
from youpy.concurrency import ReadWriteLock


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

class EngineSprite:
    """Hold the data of a Sprite as used internally by the engine.

    We use the "native" coordinate system in this class (eg. top-left corner
    as used by pygame) for performance reason (it is rendered more often that
    it is modified).
    """

    def __init__(self, path, coordsys_name="center", scene=None):
        self._path = Path(path)
        assert self._path.is_dir()
        self.images = []
        self._index = -1
        if not isinstance(scene, EngineScene):
            raise TypeError("scene must be EngineScene, not {}"
                            .format(type(scene).__name__))
        self.scene = scene
        self._position = Point.null()
        self._rect = None
        self._visible = True
        self._direction = 0 # direction angle in degree

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._path.name

    def __repr__(self):
        return "".join((f"EngineSprite(name={self.name!r})",
                        ", ".join((f"name={self.name!r}",
                                   f"visible={self._visible!r}",
                                   f"position=({self._position.tuple!r}",
                                   f"direction={self._direction!r}",
                                   )),
                        ")"))

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, new_rect):
        self._rect = new_rect

    def go_to(self, x, y):
        p = self._position
        if x is None:
            x = p.x
        if y is None:
            y = p.y
        self._position.x = x
        self._position.y = y
        self._update_rect_position()

    def go_to_position(self, position):
        self._position = position
        self._update_rect_position()

    def _update_rect_position(self):
        self.scene.coordsys.set_rect_position(self._rect, self._position)

    @property
    def position(self):
        return self._position

    @property
    def current_image(self):
        return self.images[self._index]

    def show(self):
        self._visible = True

    def hide(self):
        self._visible = False

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visible):
        self._visible = visible

    def point_in_direction(self, angle):
        self._direction = angle

    def direction(self):
        return self._direction

    def turn_counter_clockwise(self, angle):
        self._direction = self.scene.anglesys.inc_angle(self._direction, angle)

    def move_by(self, step_x, step_y):
        self.go_to(self._position.x + step_x, self._position.y + step_y)

    def move_by_velocity(self, velocity):
        self.move_by(velocity.x, velocity.y)

    def get_velocity_from_direction(self):
        return self.scene.coordsys.vector_from(Point.toward(self._direction))

    def get_state(self):
        class State:
            visible = self._visible
            rect = self._rect.copy()
            position = self._position.copy()
            direction = self.direction()
        return State()

def scale_sprite_by(sprite, ratio=None):
    """
    Operate in place!
    """
    for image in sprite.images:
        scale_image_by(image, ratio=ratio)
    sprite.rect.size = sprite.current_image.rect.size

class EngineScene:
    """Internal scene representation."""

    DEFAULT_WIDTH = 480
    DEFAULT_HEIGHT = 360

    # Sentinel object to mark scene edge in collision list.
    EDGE = object()

    def __init__(self):
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT
        self.surface = None
        self.backdrops = OrderedDict() # important to support "next backdrop"
        self._backdrop = None
        self.coordsys = None # set at configuration time
        self.anglesys = None # set at configuration time

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

class EngineMouse:

    def __init__(self):
        self._read_write_lock = ReadWriteLock()
        self._read_lock = ReadLock(self._read_write_lock)
        self._write_lock = WriteLock(self._read_write_lock)
        self._position = [None] * 2
        self._buttons = [None] * 3

    @property
    def position(self):
        with self._read_lock:
            # Calling tuple actually do the copy.
            # The value contains in the tuple are all int or bool. They
            # are immutable so they can safely be accessed concurrently.
            return tuple(self._position)

    @position.setter
    def position(self, position):
        with self._write_lock:
            self._set_position(position)

    def _set_position(self, position):
        # Enforce copy of each items.
        self._position[0], self._position[1] = position

    @property
    def buttons(self):
        with self._read_lock:
            # Calling tuple actually do the copy.
            # The value contains in the tuple are all int or bool. They
            # are immutable so they can safely be accessed concurrently.
            return tuple(self._buttons)

    @buttons.setter
    def buttons(self, buttons):
        with self._write_lock:
            # Enforce copy of each items.
            self._buttons[0], self._buttons[1], self._buttons[2] = buttons

    def set_button(self, index, pressed):
        with self._write_lock:
            self._set_button(index, pressed)

    def _set_button(self, index, pressed):
        self._buttons[index - 1] = pressed

    def process_events(self, events):
        """Update state from the given events.

        The advantage of this function is that it takes only once the
        write lock.
        """
        if not events:
            return
        with self._write_lock:
            for e in events:
                if e.type == pygame.MOUSEMOTION:
                    self._set_position(e.pos)
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self._set_button(e.button, True)
                elif e.type == pygame.MOUSEBUTTONUP:
                    self._set_button(e.button, False)
