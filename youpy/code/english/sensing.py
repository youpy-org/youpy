# -*- encoding: utf-8 -*-
"""
"""


from youpy._engine import get_scene
from youpy._engine import send_request
from youpy._engine import get_context_sprite_name
from youpy._engine import message


def touched_objects():
    sprite_name = get_context_sprite_name()
    return send_request(message.SpriteGetCollision(name=sprite_name))

def touching(object):
    return object in touched_objects()

__all__ = (
    "touched_objects",
    "touching",
)
