# -*- encoding: utf-8 -*-
"""
"""


import pygame

from funpyschool._project import Project
from funpyschool._engine.tools import FrequencyMeter
from funpyschool._engine.data import Color
from funpyschool._engine.events import EventSet
from funpyschool._engine.loader import Loader
from funpyschool._engine.configurer import Configurer


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

class ConsoleProgress:

    def in_section(self, name, index, path):
        print(f"\ro {name:10s} : {index+1: 4d}", end="")

    def end_section(self):
        print() # flush

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
        self.events = EventSet()

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
