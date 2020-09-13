# -*- encoding: utf-8 -*-
"""Front-end control routines in English.
"""


from youpy.api import StopScript
from youpy.api import run as _run
from youpy.api import get_script_logger
from youpy.api import send_request
from youpy.api import message
from youpy import logging


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
    send_request(message.Wait(delay=delay))

def stop():
    raise StopScript()

def stop_program(reason=""):
    send_request(message.StopProgram(reason=reason))

class Console:
    """Allow to print message with different severity to the console.
    """

    def debug(self, *args, **kwargs):
        return get_script_logger().log(logging.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs):
        return get_script_logger().log(logging.INFO, *args, **kwargs)

    def warning(self, *args, **kwargs):
        return get_script_logger().log(logging.WARNING, *args, **kwargs)

    def error(self, *args, **kwargs):
        return get_script_logger().log(logging.ERROR, *args, **kwargs)

    def fatal(self, *args, **kwargs):
        return get_script_logger().log(logging.FATAL, *args, **kwargs)

    def print(self, *args, **kwargs):
        return get_script_logger().log(logging.PRINT, *args, **kwargs)

console = Console()

__all__ = (
    "console",
    "run",
    "stop",
    "stop_program",
    "wait",
)
