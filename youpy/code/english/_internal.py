# -*- encoding: utf-8 -*-
"""
"""


from youpy.api import Sprite
from youpy.api import get_context_frontend_sprite


def wrap_sprite_method(name, modulename):
    def f(*args, **kwargs):
        return getattr(get_context_frontend_sprite(), name)(*args, **kwargs)
    f.__name__ = name
    f.__qualname__ = name
    f.__module__ = modulename
    method = getattr(Sprite, name)
    f.__doc__ = method.__doc__
    f.__doc__ = method.__annotations__
    return f
