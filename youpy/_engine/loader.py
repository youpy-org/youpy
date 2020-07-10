# -*- encoding: utf-8 -*-
"""
"""


from pathlib import Path
from importlib import import_module
import operator
from collections.abc import Callable

from .data import Image
from .data import Sprite
from .event import try_make_event
from .event import EVENT_FUNC_PREFIX
from .event import EventHandler


def _add_item_to_dict(d, obj):
    assert " " not in obj.name
    d[obj.name] = obj

class Loader:

    def __init__(self, progress=None):
        self.progress = progress or DummyProgress()

    def load(self, engine):
        self._load_backdrops(engine)
        self._load_sprites(engine)

    def _load_backdrops(self, engine):
        for i, path in enumerate(iter_images_set(engine.project.stage_dir)):
            _add_item_to_dict(engine.scene.backdrops, Image(path))
            self.progress.in_section("backdrops", i, path)
        load_event_handlers_to(
            engine.event_manager.event_handlers,
            import_module(engine.project.stage_module_path))
        self.progress.end_section()

    def _load_sprites(self, engine):
        for i, path in enumerate(engine.project.iter_sprite_dirs()):
            sprite = Sprite(path)
            load_sprite_images(sprite)
            load_event_handlers_to(
                engine.event_manager.event_handlers,
                import_module(engine.project.sprite_module_path(sprite.name)),
                sprite=sprite)
            _add_item_to_dict(engine.sprites, sprite)
            self.progress.in_section("sprites", i, path)
        self.progress.end_section()

class DummyProgress:

    def in_section(self, name, index, path):
        pass

    def end_section(self):
        pass

def iter_images_set(path):
    path = Path(path)
    assert path.is_dir()
    for p in path.iterdir():
        if p.suffix in (".png", ".jpg"):
            yield p

def load_images_set(path):
    l = [Image(p) for p in iter_images_set(path)]
    l.sort(key=operator.attrgetter("index"))
    return l

def load_sprite_images(sprite):
    sprite.images = load_images_set(sprite.path)
    assert len(sprite.images) > 0
    sprite._index = 0
    # Copy the image's rect so that later change in sprite's rect does not
    # affect it.
    sprite.rect = sprite.current_image.rect.copy()

def load_event_handlers_to(event_handlers, mod, sprite=None):
    """
    Arguments:
      sprite: might be None for the stage.
    """
    for attr in dir(mod):
        if attr.startswith(EVENT_FUNC_PREFIX):
            obj = getattr(mod, attr)
            if isinstance(obj, Callable) and hasattr(obj, "__name__"):
                event = try_make_event(obj.__name__)
                if event is None:
                    raise RuntimeError(f"invalid event name: '{attr}'")
                event_handlers.register(
                    event,
                    EventHandler(obj, sprite=sprite))
