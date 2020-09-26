# -*- encoding: utf-8 -*-
"""
"""


from collections.abc import MutableMapping
from collections import OrderedDict


class SharedVariable:

    def __init__(self, shared_variable_set, value):
        self._set = shared_variable_set
        self._value = value
        self._visible = False

    def get(self):
        return self._value

    def hide(self):
        if not self._visible:
            return
        self._visible = False
        self._set_changed()

    def show(self):
        if self._visible:
            return
        self._visible = True
        self._set_changed()

    def __iadd__(self, other):
        old_value = self._value
        self._value += other
        if old_value != self._value:
            self._set_changed()
        return self

    def _set_changed(self):
        self._set._changed = True

class SharedVariableSet(MutableMapping):

    def __init__(self):
        self._d = OrderedDict()
        self._changed = False

    def __setitem__(self, name, value):
        self._d[name] = SharedVariable(self, value)
        self._changed = True

    def __getitem__(self, name):
        return self._d[name]

    def __delitem__(self, name):
        del self._d[name]
        self._changed = True

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    @property
    def has_changed(self):
        return self._changed

    def clear_change_flag(self):
        self._changed = False
