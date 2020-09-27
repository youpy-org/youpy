# -*- encoding: utf-8 -*-
"""Sub-commands package.
"""


from importlib import import_module
import os


CMD_DIR = os.path.dirname(__file__)

def is_command_module(path):
    return path.endswith(".py") \
        and (not os.path.basename(path).startswith("_"))

def iter_command_names():
    return (filename[:-3]
            for filename in os.listdir(CMD_DIR)
            if is_command_module(os.path.join(CMD_DIR, filename)))

class CommandNotFoundError(Exception):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "command not found: {}".format(self.name)

def import_command(name):
    fullname = "{}.{}".format(__name__, name)
    try:
        return import_module(fullname)
    except ModuleNotFoundError as e:
        if e.name == fullname:
            raise CommandNotFoundError(name)
        raise e
