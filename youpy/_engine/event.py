# -*- encoding: utf-8 -*-
"""
"""


import re
from collections import defaultdict

from youpy._tools import IDENT_PATTERN
from youpy.keys import check_key


EVENT_FUNC_PREFIX = "when_"

class EventHandlers:

    def __init__(self):
        self._handlers = defaultdict(lambda: defaultdict(list))

    def register(self, event, handler):
        # print(f"add event handler {event!r}")
        self._handlers[type(event).__name__][event].append(handler)

    def iter_all(self, event_type):
        if not issubclass(event_type, Event):
            raise TypeError("event_type must be a subclass of Event, but got {}"
                            .format(event_type))
        for v in self._handlers[event_type.__name__].values():
            yield from v

    def get(self, event):
        if isinstance(event, Event):
            return self._handlers[type(event).__name__][event]
        else:
            raise TypeError("obj must be Event, not {}"
                            .format(type(event).__name__))

class MetaEvent(type):

    types = []

    def __new__(metacls, name, bases, namespace, **kwds):
        cls = super().__new__(metacls, name, bases, namespace, **kwds)
        if name == "Event":
            return cls
        metacls.types.append(cls)
        pattern = EVENT_FUNC_PREFIX + getattr(cls, "pattern")
        cls.regex = re.compile(pattern)
        cls._decl_attrs = cls.regex.groupindex.keys()
        return cls

class Event(object, metaclass=MetaEvent):

    __slots__ = ("_hash_value", "_attrs")

    def __init__(self, **attrs):
        self._attrs = attrs
        self._hash_value = tuple(attrs[k] for k in sorted(attrs.keys()))
        for attr_name in self._decl_attrs:
            if attr_name not in self._attrs:
                raise TypeError(f"unexpected keyword argument '{attr_name}'")

    def __hash__(self):
        return hash(self._hash_value)

    def __repr__(self):
        return "{}({})".format(
            type(self).__name__,
            ", ".join(f"{k}={self._attrs[k]!r}" for k in sorted(self._attrs)))

    def __getattr__(self, name):
        try:
            return self._attrs[name]
        except KeyError:
            raise AttributeError(name)

class BackdropSwitches(Event):
    pattern = r"backdrop_switches_to_(?P<backdrop>%(ident)s)" \
        % dict(ident=IDENT_PATTERN)

class KeyPressed(Event):
    pattern = r"(?P<key>\w*)_key_pressed"

    def __init__(self, key=None):
        key = key.lower()
        check_key(key)
        super().__init__(key=key)

class ProgramStart(Event):
    pattern = r"program_start"

class EventHandler:

    def __init__(self, callback, sprite=None):
        assert callback is not None
        self.callback = callback
        self.sprite = sprite

def try_make_event(handler_name):
    for event_type in Event.types:
        mo = event_type.regex.fullmatch(handler_name)
        if mo:
            try:
                return event_type(**mo.groupdict())
            except Exception as e:
                raise ValueError(
                    f"invalid event handler: '{handler_name}' - {e}")
