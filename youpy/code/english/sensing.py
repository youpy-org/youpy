# -*- encoding: utf-8 -*-
"""
"""


from ._internal import wrap_sprite_method

from youpy.api import get_scene
from youpy.api import send_request
from youpy.api import SCENE_EDGE


class Scene:
    """User interface to the scene read-only attributes.

    WARNING: Make sure everything is read-only since they are accessed
             concurrently.
    """

    # Make sure we have no attribute otherwise a lock will be required.
    __slots__ = ()

    @property
    def width(self):
        return get_scene().scene.width

    @property
    def height(self):
        return get_scene().scene.height

    @property
    def edge(self):
        return SCENE_EDGE

scene = Scene()

sprite_functions = (
    "touched_objects",
    "touching",
    )

for name in sprite_functions:
    def modulename(): pass # only need to get the current module name
    globals()[name] = wrap_sprite_method(name, modulename.__module__)
del name, modulename

__all__ = sprite_functions + (
    "scene",
    "touched_objects",
    "touching",
)

del sprite_functions
