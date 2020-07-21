# -*- encoding: utf-8 -*-
"""Front-end variable routines in English.
"""


from youpy._engine.api import send_request
from youpy._engine import message


class SharedVariable:

    def __init__(self, name, value):
        self._name = name
        self._value = value

    @property
    def value(self):
        return self._value

    def hide(self):
        return send_request(message.SharedVariableOp(name=self._name,
                                                     op="hide"))

    def show(self):
        return send_request(message.SharedVariableOp(name=self._name,
                                                     op="show"))

    def __iadd__(self, other):
        send_request(message.SharedVariableOp(name=self._name,
                                              op="__iadd__",
                                              args=(other,)))
        return self

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self._name!r}, value={self._value!r})"

class SharedVariableSet:
    """Holds the set of the shared variables proxy.

    WARNING: This class is a singleton and is accessed concurrently. Do not
             store any unprotected (by a lock) attributes in there.
    """

    # Make sure we have no attribute otherwise a lock will be required.
    __slots__ = ()

    def __getattr__(self, name):
        try:
            value = send_request(message.SharedVariableOp(name=name, op="get"))
        except KeyError:
            raise AttributeError(f"undefined shared variable '{name}'")
        else:
            return SharedVariable(name, value)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            return super().__setattr__(name, value)
        # When executing code like "shared_variable.score += 1",
        # __setattr__ is called with name="score" and value="value returned by
        # __iadd__". In such case, the in-place operation have already been
        # committed, thus it is useless to create a new variable.
        if isinstance(value, SharedVariable):
            return
        send_request(message.SharedVariableNew(name=name, value=value))

    def __delattr__(self, name):
        try:
            send_request(message.SharedVariableDel(name))
        except KeyError:
            raise AttributeError(f"undefined shared variable '{name}'")

shared_variable = SharedVariableSet()

__all__ = (
    "shared_variable",
)
