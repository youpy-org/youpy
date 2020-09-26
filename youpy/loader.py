# -*- encoding: utf-8 -*-
"""
"""


from pathlib import Path
from importlib import import_module
import operator
from collections.abc import Callable

from .data import Image
from .data import EngineSprite
from .event import try_make_event
from .event import EVENT_FUNC_PREFIX
from .event import EventHandler

from youpy import logging
LOGGER = logging.getLogger(__name__)


def _add_item_to_dict(d, obj):
    assert " " not in obj.name
    d[obj.name] = obj

class Loader:

    def __init__(self, progress=None):
        self.progress = progress or DummyProgress()

    def load(self, simu):
        self._load_backdrops(simu)
        self._load_sprites(simu)

    def _load_backdrops(self, simu):
        if not simu.project.stage_dir.is_dir():
            LOGGER.warning("no stage script found")
            return
        for i, path in enumerate(list_images_set(simu.project.stage_dir)):
            _add_item_to_dict(simu.scene.backdrops, Image(path))
            self.progress.in_section("backdrop", i, path)
        load_event_handlers_to(
            simu.event_manager.event_handlers,
            import_module(simu.project.stage_module_path))
        self.progress.end_section()

    def _load_sprites(self, simu):
        for i, path in enumerate(simu.project.list_sprite_dirs()):
            sprite = EngineSprite(path, scene=simu.scene)
            load_sprite_images(sprite)
            load_event_handlers_to(
                simu.event_manager.event_handlers,
                import_module(simu.project.sprite_module_path(sprite.name)),
                sprite=sprite)
            simu.sprites.add(sprite)
            self.progress.in_section("sprite", i, path)
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

def list_images_set(path):
    l = list(iter_images_set(path))
    l.sort()
    return l

def load_images_set(path):
    l = [Image(p) for p in list_images_set(path)]
    l.sort(key=operator.attrgetter("index"))
    return l

def load_sprite_images(sprite):
    if not isinstance(sprite, EngineSprite):
        raise TypeError("sprite must be EngineSprite, not {}"
                        .format(type(sprite).__name__))
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
