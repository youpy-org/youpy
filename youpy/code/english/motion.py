# -*- encoding: utf-8 -*-
"""
"""


from ._internal import wrap_sprite_method


__all__ = (
    "bounce_if_on_edge",
    "change_x_by",
    "change_y_by",
    "direction",
    "glide",
    "go_to",
    "move",
    "move_by",
    "point_in_direction",
    "position",
    "set_x_to",
    "set_y_to",
    "turn_clockwise",
    "turn_counter_clockwise",
    "x_position",
    "y_position",
)

for name in __all__:
    def modulename(): pass # only need to get the current module name
    globals()[name] = wrap_sprite_method(name, modulename.__module__)
del name, modulename
