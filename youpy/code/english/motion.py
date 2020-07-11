# -*- encoding: utf-8 -*-
"""
"""


import math

from youpy._engine import get_scene
from youpy._engine import send_request
from youpy._engine import get_context_sprite_name
from youpy._engine import message
from youpy._tools import degree_to_radian
from youpy._tools import radian_to_degree


def go_to(x, y):
    """Change sprite position to _x_ and _y_."""
    if not isinstance(x, int):
        raise TypeError("x must be int, not {}"
                        .format(type(x).__name__))
    if not isinstance(y, int):
        raise TypeError("y must be int, not {}"
                        .format(type(y).__name__))
    sprite_name = get_context_sprite_name()
    send_request(message.SpriteOp(
        name=sprite_name,
        op="go_to",
        args=get_scene()._coordsys.point_from(x, y)))

def set_x_to(x):
    if not isinstance(x, int):
        raise TypeError("x must be int, not {}"
                        .format(type(x).__name__))
    sprite_name = get_context_sprite_name()
    send_request(message.SpriteOp(
        name=sprite_name,
        op="go_to",
        args=(get_scene()._coordsys.abscissa_from(x), None)))

def set_y_to(y):
    if not isinstance(y, int):
        raise TypeError("y must be int, not {}"
                        .format(type(y).__name__))
    sprite_name = get_context_sprite_name()
    send_request(message.SpriteOp(
        name=sprite_name,
        op="go_to",
        args=(None, get_scene()._coordsys.ordinate_from(y))))

def move_by(step_x, step_y):
    """Change sprite position by _step_x_ and _step_y_."""
    if not isinstance(step_x, int):
        raise TypeError("step_x must be int, not {}"
                        .format(type(step_x).__name__))
    if not isinstance(step_y, int):
        raise TypeError("step_y must be int, not {}"
                        .format(type(step_y).__name__))
    sprite_name = get_context_sprite_name()
    send_request(message.SpriteOp(
        name=sprite_name,
        op="move_by",
        args=(step_x, step_y)))

def change_x_by(step_x):
    if not isinstance(step_x, int):
        raise TypeError("step_x must be int, not {}"
                        .format(type(step_x).__name__))
    sprite_name = get_context_sprite_name()
    send_request(message.SpriteOp(
        name=sprite_name,
        op="move_by",
        args=(step_x, 0)))

def change_y_by(step_y):
    if not isinstance(step_y, int):
        raise TypeError("step_y must be int, not {}"
                        .format(type(step_y).__name__))
    sprite_name = get_context_sprite_name()
    send_request(message.SpriteOp(
        name=sprite_name,
        op="move_by",
        args=(0, step_y)))

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

def _get_state_for(sprite_name):
    return send_request(message.SpriteOp(name=sprite_name, op="get_state"))

def _get_state():
    sprite_name = get_context_sprite_name()
    return _get_state_for(sprite_name)

def position():
    return get_scene()._coordsys.point_to(*_get_state().position())

def x_position():
    return position()[0]

def y_position():
    return position()[1]

def direction():
    return get_scene()._anglesys.from_degree(_get_state().direction())

def bounce_if_on_edge():
    sprite_name = get_context_sprite_name()
    st = _get_state_for(sprite_name)
    angle = degree_to_radian(st.direction())
    r = st.rect
    scene = get_scene()
    if r.left < 0 or r.right > scene.width: # vertical edges
        new_angle = math.atan2(math.sin(angle), -math.cos(angle))
    elif r.top < 0 or r.bottom > scene.height: # horizontal edges
        new_angle = math.atan2(-math.sin(angle), math.cos(angle))
    else: # no collision
        return
    send_request(message.SpriteBatchOp(
        name=sprite_name,
        ops=(
            dict(op="point_in_direction",
                 args=(int(round(radian_to_degree(new_angle))) % 360,)),
        )))

__all__ = (
    "bounce_if_on_edge",
    "change_x_by",
    "change_y_by",
    "direction",
    "go_to",
    "move",
    "move_by",
    "point_in_direction",
    "position",
    "set_x_to",
    "set_y_to",
    "x_position",
    "y_position",
)