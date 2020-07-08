# -*- encoding: utf-8 -*-
"""Front-end API functions of the "looks" category.
"""


from youpy._engine import send_request
from youpy._engine import message


def switch_to(backdrop):
    # TODO(Nicolas Despres): Add wait keyword argument to mimic the
    #   "switch to <backdrop> and wait" block?
    if not isinstance(backdrop, str):
        raise TypeError("backdrop must be str, not {}"
                        .format(type(backdrop).__name__))
    send_request(message.BackdropSwitchTo(name=backdrop))

__all__ = (
    "switch_to",
)
