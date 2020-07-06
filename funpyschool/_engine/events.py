# -*- encoding: utf-8 -*-
"""
"""


import re
from collections import defaultdict

from funpyschool._tools import IDENT_PATTERN


EVENT_FUNC_PREFIX = "when_"

class EventSet:

    def __init__(self):
        self._events = defaultdict(list)

    def add(self, event):
        self._events[type(event).__name__].append(event)

    _ATTR_SUFFIX = "Events"

    def __getattr__(self, attr):
        if attr.endswith(self._ATTR_SUFFIX):
            name = attr[:-len(self._ATTR_SUFFIX)]
            if name in self._events:
                return self._events[name]
        raise AttributeError(attr)

class MetaEvent(type):

    types = []

    def __new__(metacls, name, bases, namespace, **kwds):
        cls = super().__new__(metacls, name, bases, namespace, **kwds)
        if name == "Event":
            return cls
        metacls.types.append(cls)
        pattern = EVENT_FUNC_PREFIX + getattr(cls, "pattern")
        cls.regex = re.compile(pattern)
        cls.__slots__ = tuple(cls.regex.groupindex.keys())
        return cls

class Event(object, metaclass=MetaEvent):

    def __init__(self, sprite=None, callback=None, **kwargs):
        self.sprite = sprite
        if callback is None:
            raise ValueError("callback event must be passed")
        self.callback = callback
        for k, v in kwargs.items():
            if v is None:
                raise ValueError(f"None value for event attribute '{k}'")
            setattr(self, k, v)

class BackdropSwitches(Event):
    pattern = r"backdrop_switches_to_(?P<backdrop>%(ident)s)" \
        % dict(ident=IDENT_PATTERN)

class KeyPressed(Event):
    pattern = r"(?P<key>\w*)_key_pressed"

class ProgramStart(Event):
    pattern = r"program_start"

def try_make_event(callback, sprite=None):
    for event_type in Event.types:
        mo = event_type.regex.fullmatch(callback.__name__)
        if mo:
            return event_type(sprite=sprite,
                              callback=callback,
                              **mo.groupdict())
