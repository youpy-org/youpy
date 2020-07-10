# -*- encoding: utf-8 -*-
"""
"""


from youpy._engine import get_scene
from youpy._engine import send_request
from youpy._engine import get_context_sprite_name
from youpy._engine import message


def go_to(x, y):
    """Change sprite position to _x_ and _y_."""
    sprite_name = get_context_sprite_name()
    send_request(message.SpriteOp(
        name=sprite_name,
        op="go_to",
        args=get_scene()._coordsys.point_from(x, y)))

def point_in_direction(angle):
    sprite_name = get_context_sprite_name()
    send_request(message.SpriteOp(
        name=sprite_name,
        op="point_in_direction",
        args=(angle,)))

__all__ = (
    "go_to",
    "point_in_direction",
)
