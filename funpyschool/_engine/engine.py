# -*- encoding: utf-8 -*-
"""
"""


from pathlib import Path
import json

import pygame

from funpyschool._engine import coordsys
from funpyschool._engine.tools import FrequencyMeter
from funpyschool._engine.media import Color
from funpyschool._engine.media import Image
from funpyschool._engine.media import iter_images_set
from funpyschool._engine.sprite import Sprite
from funpyschool._engine.sprite import scale_sprite_by


class Project:

    STAGE_DIR = "stage"

    def __init__(self, path):
        self._path = Path(path)

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._path.name

    @property
    def stage_dir(self):
        return self._path / self.STAGE_DIR

    def iter_backdrop_images(self):
        yield from iter_images_set(self.stage_dir)

    def iter_sprite_dirs(self):
        for p in self._path.iterdir():
            if p.name != self.STAGE_DIR and p.is_dir():
                yield p

    @property
    def config_file(self):
        return self._path / "config.json"

class Scene:

    def __init__(self):
        self.width = 480
        self.height = 360
        self.surface = None
        self.backdrops = {}
        self.backdrop = None

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def rect(self):
        return pygame.Rect(0, 0, self.width, self.height)

    def init(self):
        self.surface = pygame.display.set_mode(self.size)

    @property
    def center(self):
        return (self.width // 2, self.height // 2)

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
        for i, path in enumerate(engine.project.iter_backdrop_images()):
            _add_item_to_dict(engine.scene.backdrops, Image(path))
            self.progress.in_section("backdrops", i, path)
        self.progress.end_section()

    def _load_sprites(self, engine):
        for i, path in enumerate(engine.project.iter_sprite_dirs()):
            _add_item_to_dict(engine.sprites, Sprite(path))
            self.progress.in_section("sprites", i, path)
        self.progress.end_section()

class DummyProgress:

    def in_section(self, name, index, path):
        pass

    def end_section(self):
        pass

class ConsoleProgress:

    def in_section(self, name, index, path):
        print(f"\ro {name:10s} : {index+1: 4d}", end="")

    def end_section(self):
        print() # flush

class FunPySchoolException(Exception):
    pass

class ConfigError(FunPySchoolException):
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
                scene.backdrop = scene.backdrops[initial_backdrop]
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

class Renderer:

    def __init__(self):
        self.fps = FrequencyMeter()

    def render(self, engine):
        self._render_scene(engine.scene)
        self._render_sprites(engine.scene, engine.sprites)
        if self.fps.update():
            print("FPS:", self.fps)
        engine._flip()

    def _render_scene(self, scene):
        if scene.backdrop is None:
            scene.surface.fill(Color.black._c)
        else:
            scene.surface.blit(scene.backdrop.surface, (0, 0))

    def _render_sprites(self, scene, sprites):
        for sprite in sprites.values():
            self._render_sprite(scene, sprite)

    def _render_sprite(self, scene, sprite):
        if not sprite.visible:
            return
        scene.surface.blit(sprite.current_image.surface, sprite.rect)

class Engine:

    def __init__(self, project):
        self.project = project
        self.scene = Scene()
        self.sprites = {}
        self._is_running = False

    @property
    def is_running(self):
        return self._is_running

    def run(self):
        if self._is_running:
            raise RuntimeError("engine already running")
        self._is_running = True
        try:
            print(f"Initializing {self.project.name}...")
            pygame.init()
            pygame.display.set_caption(self.project.name)
            self.scene.init()
            self._load()
            self._configure()
            self._renderer = Renderer()
            self._loop()
        finally:
            self._is_running = False

    def _flip(self):
        pygame.display.flip()

    LOAD_BACK_COLOR = Color(62, 254, 165)

    def _load(self):
        print("Loading...")
        self.scene.surface.fill(self.LOAD_BACK_COLOR._c)
        self._flip()
        Loader(progress=ConsoleProgress()).load(self)

    def _configure(self):
        print("Configuring...")
        Configurer(self).configure()

    def _loop(self):
        while self._is_running:
            for event in pygame.event.get():
                # print(type(event), event)
                if event.type == pygame.QUIT \
                   or (event.type == pygame.KEYUP
                       and event.key == pygame.K_ESCAPE):
                    self._is_running = False
                # elif event.type == pygame.MOUSEMOTION:
                #     MOUSE._set_pos(*event.pos)
            self._render()

    def _render(self):
        self._renderer.render(self)
