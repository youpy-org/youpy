# -*- encoding: utf-8 -*-
"""Front-end API functions of the "looks" category.
"""


from youpy._engine import get_running_engine
from youpy._engine import send_request
from youpy._engine import get_context_sprite_name
from youpy._engine import message


class Scene:
    """User interface to the scene read-only attributes.

    WARNING: Make sure everything is read-only since they are accessed
             concurrently.
    """

    # Make sure we have no attribute otherwise a lock will be required.
    __slots__ = ()

    @property
    def width(self):
        return get_running_engine().scene.width

    @property
    def height(self):
        return get_running_engine().scene.height

scene = Scene()

def switch_to(backdrop):
    # TODO(Nicolas Despres): Add wait keyword argument to mimic the
    #   "switch to <backdrop> and wait" block?
    if not isinstance(backdrop, str):
        raise TypeError("backdrop must be str, not {}"
                        .format(type(backdrop).__name__))
    send_request(message.BackdropSwitchTo(name=backdrop))

def show():
    """Show the current sprite."""
    sprite_name = get_context_sprite_name()
    send_request(message.SpriteOp(name=sprite_name, op="show"))

def hide():
    """Hide the current sprite."""
    sprite_name = get_context_sprite_name()
    send_request(message.SpriteOp(name=sprite_name, op="hide"))

__all__ = (
    "hide",
    "show",
    "switch_to",
)
