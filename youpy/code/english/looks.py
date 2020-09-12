# -*- encoding: utf-8 -*-
"""Front-end API functions of the "looks" category.
"""


from ._internal import wrap_sprite_method

from youpy.api import send_request
from youpy.api import message


def switch_backdrop_to(backdrop):
    # TODO(Nicolas Despres): Add wait keyword argument to mimic the
    #   "switch to <backdrop> and wait" block?
    if not isinstance(backdrop, str):
        raise TypeError("backdrop must be str, not {}"
                        .format(type(backdrop).__name__))
    send_request(message.BackdropSwitchTo(name=backdrop))

sprite_functions = (
    "hide",
    "show",
    )

for name in sprite_functions:
    def modulename(): pass # only need to get the current module name
    globals()[name] = wrap_sprite_method(name, modulename.__module__)
del name, modulename

__all__ = sprite_functions + (
    "switch_backdrop_to",
)

del sprite_functions
