# -*- encoding: utf-8 -*-
"""
"""


from ._internal import wrap_sprite_method

from youpy.api import get_scene
from youpy.api import send_request


class StageType:

    def __getattr__(self, name):
        return getattr(get_scene(), name)

Stage = StageType()

sprite_functions = (
    "touched_objects",
    "touching",
    )

for name in sprite_functions:
    def modulename(): pass # only need to get the current module name
    globals()[name] = wrap_sprite_method(name, modulename.__module__)
del name, modulename

__all__ = sprite_functions + (
    "Stage",
)

del sprite_functions
