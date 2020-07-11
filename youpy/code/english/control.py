# -*- encoding: utf-8 -*-
"""Front-end control routines in English.
"""


import time

from youpy._engine.script import StopScript


def run(caller_locals=None, **kwargs):
    # The call is to get rid of the call to locals() in the caller.
    #FIXME: weirdly make the engine run twice...
    # if caller_scope is None:
    #     import inspect
    #     caller_scope = inspect.stack()[-1].frame.f_locals
    if caller_locals.get("__name__") != "__main__":
        return
    import youpy
    youpy.run(caller_locals["__file__"], **kwargs)

def wait(delay):
    time.sleep(delay)

def stop():
    raise StopScript()

__all__ = (
    "run",
    "stop",
    "wait",
)
