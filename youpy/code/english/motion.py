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
        args=(get_scene()._anglesys.to_degree(angle),)))

def move(step):
    sprite_name = get_context_sprite_name()
    send_request(message.SpriteOp(
        name=sprite_name,
        op="move",
        args=(step,)))

def _get_state():
    sprite_name = get_context_sprite_name()
    return send_request(message.SpriteOp(name=sprite_name, op="get_state"))

def position():
    return get_scene()._coordsys.point_to(*_get_state().position())

def x_position():
    return position()[0]

def y_position():
    return position()[1]

def direction():
    return get_scene()._anglesys.from_degree(_get_state().direction())

__all__ = (
    "direction",
    "go_to",
    "move",
    "point_in_direction",
    "position",
    "x_position",
    "y_position",
)
