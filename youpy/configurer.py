# -*- encoding: utf-8 -*-
"""
"""


import json

from .error import YoupyException
from .math import CoordSys
from .math import AngleSys
from .data import scale_sprite_by
from .math import Point

from youpy import logging
LOGGER = logging.getLogger(__name__)


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
        self._configure_scene(self.engine.scene, cfg.get("scene", {}))
        self._configure_sprites(self.engine.sprites, cfg.get("sprites"),
                                self.engine.scene.coordsys)

    def _configure_coordsys(self, scene, cfg):
        coordsys_name = cfg.get("coordinate_system", CoordSys.DEFAULT)
        LOGGER.info(f"{coordsys_name} coordinate system")
        try:
            coordsys_class = CoordSys.get_system(coordsys_name)
        except KeyError:
            raise ConfigError(f"invalid coordinate system: '{coordsys_name}'")
        else:
            scene.coordsys = coordsys_class(getattr(scene, coordsys_name))

    def _configure_anglesys(self, scene, cfg):
        anglesys_name = cfg.get("angle_system", AngleSys.DEFAULT)
        try:
            anglesys_class = AngleSys.get_system(anglesys_name)
        except AttributeError:
            raise ConfigError(f"invalid angle system: '{anglesys_name}'")
        else:
            scene.anglesys = anglesys_class()

    def _configure_scene(self, scene, cfg):
        assert cfg is not None
        self._configure_coordsys(scene, cfg)
        self._configure_anglesys(scene, cfg)
        initial_backdrop = cfg.get("initial_backdrop")
        if initial_backdrop is not None:
            try:
                scene.backdrop = initial_backdrop
            except KeyError:
                raise ConfigError(
                    f"invalid initial backdrop: '{initial_backdrop}'")

    def _configure_sprites(self, sprites, cfg, coordsys):
        if cfg is None:
            return
        for sprite_name, sprite_cfg in cfg.items():
            try:
                sprite = sprites[sprite_name]
            except KeyError:
                raise ConfigError(f"unknown sprite: '{sprite_name}'")
            else:
                self._configure_sprite(sprite, sprite_cfg, coordsys)

    def _configure_sprite(self, sprite, cfg, coordsys):
        sprite.coordsys_name = coordsys.get_name()
        ratio = cfg.get("ratio")
        scale_sprite_by(sprite, ratio=ratio)
        position = cfg.get("position")
        if position is not None:
            sprite.go_to(*coordsys.point_from(Point(*position)).tuple)
        visible = cfg.get("visible", None)
        if visible is not None:
            sprite.visible = visible
