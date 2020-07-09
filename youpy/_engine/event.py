# -*- encoding: utf-8 -*-
"""
"""


import re
from collections import defaultdict

from youpy._tools import IDENT_PATTERN


EVENT_FUNC_PREFIX = "when_"

class EventHandlers:

    def __init__(self):
        self._handlers = defaultdict(list)

    def register(self, event, handler):
        # print(f"register event handler for {event!r} - hash_value={event._hash_value!r} - hash={hash(event)}")
        self._handlers[event].append(handler)

    def get(self, event):
        if not isinstance(event, Event):
            raise TypeError("event must be Event, not {}"
                            .format(type(event).__name__))
        return self._handlers[event]

    def print_(self):
        for event, handlers in self._handlers.items():
            print(event)
            for handler in handlers:
                print("- ", handler)

    def __iter__(self):
        return iter(self._handlers)

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
        for attr_name in self._decl_attrs:
            if attr_name not in self._attrs:
                raise TypeError(f"unexpected keyword argument '{attr_name}'")
        self._hash_value = (
            type(self).__name__,
            *(attrs[k] for k in sorted(attrs.keys()))
        )

    def __hash__(self):
        return hash(self._hash_value)

    def __eq__(self, other):
        return self._hash_value == other._hash_value

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

class ProgramStart(Event):
    pattern = r"program_start"

class EventHandler:

    def __init__(self, callback, sprite=None):
        assert callback is not None
        self.callback = callback
        self.sprite = sprite

    def __repr__(self):
        return f"{type(self).__name__}(callback={self.callback.__name__!r}, sprite={None if self.sprite is None else self.sprite.name!r})"

    @property
    def name(self):
        return f"{'stage' if self.sprite is None else self.sprite.name}.{self.callback.__name__}"

def try_make_event(handler_name):
    for event_type in Event.types:
        mo = event_type.regex.fullmatch(handler_name)
        if mo:
            try:
                return event_type(**mo.groupdict())
            except Exception as e:
                raise ValueError(
                    f"invalid event handler: '{handler_name}' - {e}")
