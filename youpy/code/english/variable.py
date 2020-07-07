# -*- encoding: utf-8 -*-
"""Front-end variable routines in English.
"""


from youpy._engine import send_request
from youpy._engine import message


class SharedVariable:

    def __init__(self, name):
        self._name = name

    @property
    def value(self):
        return send_request(message.SharedVariableGet(name=self._name))

    def hide(self):
        return send_request(message.SharedVariableOp(name=self._name,
                                                     op="hide"))

class SharedVariableSet:

    def __init__(self):
        self._d = {}

    def __getattr__(self, name):
        try:
            return self._d[name]
        except KeyError:
            raise AttributeError(f"undefined shared variable: '{name}'")

    def __setattr__(self, name, value):
        if name.startswith("_"):
            return super().__setattr__(name, value)
        send_request(message.SharedVariableNew(name=name, value=value))
        self._d[name] = SharedVariable(name)

    def __delattr__(self, name):
        send_request(message.SharedVariableDel(name))

def hide_variable(variable):
    variable.hide()

shared_variable = SharedVariableSet()

__all__ = (
    "hide_variable",
    "shared_variable",
)
