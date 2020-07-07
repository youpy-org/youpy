# -*- encoding: utf-8 -*-
"""
"""


import json

from .error import YoupyException
from . import coordsys
from .data import scale_sprite_by


class ConfigError(YoupyException):
    pass

class Configurer:

    def __init__(self, engine):
        self.engine = engine

    def load(self, filepath):
        try:
            with open(filepath) as stream:
                return json.load(stream)
        except FileNotFoundError:
            return {}

    def configure(self):
        cfg = self.load(self.engine.project.config_file)
        self._configure_coordsys(self.engine, cfg)
        self._configure_scene(self.engine.scene, cfg.get("scene"))
        self._configure_sprites(self.engine.sprites, cfg.get("sprites"))

    def _configure_coordsys(self, engine, cfg):
        coordsys_name = cfg.get("coordinate_system", coordsys.DEFAULT)
        try:
            coordsys_class = getattr(coordsys, coordsys_name)
        except AttributeError:
            raise ConfigError(f"invalid coordinate system: '{coordsys_name}'")
        else:
            engine.coordsys = coordsys_class(engine.scene.center)

    def _configure_scene(self, scene, cfg):
        if cfg is None:
            return
        initial_backdrop = cfg.get("initial_backdrop")
        if initial_backdrop is not None:
            try:
                scene.backdrop = initial_backdrop
            except KeyError:
                raise ConfigError(
                    f"invalid initial backdrop: '{initial_backdrop}'")

    def _configure_sprites(self, sprites, cfg):
        if cfg is None:
            return
        for sprite_name, sprite_cfg in cfg.items():
            try:
                sprite = sprites[sprite_name]
            except KeyError:
                raise ConfigError(f"unknown sprite: '{sprite_name}'")
            else:
                self._configure_sprite(sprite, sprite_cfg)

    def _configure_sprite(self, sprite, cfg):
        ratio = cfg.get("ratio")
        scale_sprite_by(sprite, ratio=ratio)
        position = cfg.get("position")
        if position is not None:
            self.engine.coordsys.rect_go_to(sprite.rect,
                                            position["x"], position["y"])
        visible = cfg.get("visible", True)
        if visible:
            sprite.visible = visible
