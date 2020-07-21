# -*- encoding: utf-8 -*-
"""
"""


from youpy._engine.api import get_scene
from youpy._engine.api import send_request
from youpy._engine.api import get_context_sprite_name
from youpy._engine import message
from youpy._engine.data import SCENE_EDGE


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

def touched_objects():
    sprite_name = get_context_sprite_name()
    return send_request(message.SpriteGetCollision(name=sprite_name))

def touching(object):
    return object in touched_objects()

__all__ = (
    "scene",
    "touched_objects",
    "touching",
)
