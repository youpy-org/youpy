# -*- encoding: utf-8 -*-
"""Front-end control routines in English.
"""


import time

from youpy.api import StopScript
from youpy.api import run as _run
from youpy.api import get_script_logger


def run(caller_locals=None, **kwargs):
    # The call is to get rid of the call to locals() in the caller.
    #FIXME: weirdly make the engine run twice...
    # if caller_scope is None:
    #     import inspect
    #     caller_scope = inspect.stack()[-1].frame.f_locals
    if caller_locals.get("__name__") != "__main__":
        return
    _run(caller_locals["__file__"], **kwargs)

def wait(delay):
    time.sleep(delay)

def stop():
    raise StopScript()

class Console:
    """Allow to print message with different severity to the console.
    """

    def _log(self, tag, *args, **kwargs):
        return getattr(get_script_logger(), tag)(*args, **kwargs)

    def debug(self, *args, **kwargs):
        return self._log("debug", *args, **kwargs)

    def info(self, *args, **kwargs):
        return self._log("info", *args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._log("warning", *args, **kwargs)

    def error(self, *args, **kwargs):
        return self._log("error", *args, **kwargs)

    def fatal(self, *args, **kwargs):
        return self._log("fatal", *args, **kwargs)

console = Console()

__all__ = (
    "console",
    "run",
    "stop",
    "wait",
)
