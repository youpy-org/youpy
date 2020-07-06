# -*- encoding: utf-8 -*-
"""
"""


from pathlib import Path

from .media import load_images_set
from .media import scale_image_by


class Sprite:
    """Hold the data of a Sprite as used internally by the engine.

    We use the "native" coordinate system in this class (eg. top-left corner
    as used by pygame) for performance reason (it is rendered more often that
    it is modified).
    """

    def __init__(self, path):
        self._path = Path(path)
        assert self._path.is_dir()
        self.images = []
        self._index = -1
        self.visible = True
        self.rect = None

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._path.name

    def __repr__(self):
        return f"_engine.Sprite(name={self.name!r})"

    def go_to(self, x, y):
        self.rect.topleft = (x, y)

    @property
    def current_image(self):
        return self.images[self._index]

def load_sprite_images(sprite):
    sprite.images = load_images_set(sprite.path)
    assert len(sprite.images) > 0
    sprite._index = 0
    sprite.rect = sprite.current_image.rect

def scale_sprite_by(sprite, ratio=None):
    """
    Operate in place!
    """
    for image in sprite.images:
        scale_image_by(image, ratio=ratio)
    sprite.rect.size = sprite.current_image.rect.size
