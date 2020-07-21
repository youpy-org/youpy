# -*- encoding: utf-8 -*-
"""
"""


from collections.abc import MutableMapping
from collections import OrderedDict
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

import pygame

from youpy._project import Project
from youpy._engine.tools import FrequencyMeter
from youpy._engine.data import Color
from youpy._engine.data import _Scene
from youpy._engine.data import Scene
from youpy._engine.data import SCENE_EDGE
from youpy._engine import event
from youpy._engine.loader import Loader
from youpy._engine.configurer import Configurer
from youpy._engine.script import ScriptSet
from youpy._engine import message
from youpy._concurrency import EmptyQueue
from youpy.keys import iter_keys
from youpy.keys import check_key
from youpy._engine.loop import FixedDeltaTimeEngineLoop


class ConsoleProgress:

    def in_section(self, name, index, path):
        print(f"\ro {name:10s} : {index+1: 4d}", end="")

    def end_section(self):
        print() # flush

class FPSRenderer:

    def __init__(self, fps, engine):
        self.fps = fps
        self.engine = engine

    def update(self):
        self._surf = self.engine.default_font.render(
            f'{self.fps.frequency: 3.0f}', True, Color.white._c)
        self._rect = self._surf.get_rect().copy()
        self._rect.topleft = (self.engine.scene.width - self._rect.width, 0)
        print("FPS:", self.fps)

    def render(self):
        self.engine.scene.surface.fill(Color.black._c, self._rect)
        self.engine.scene.surface.blit(self._surf, self._rect)

class DummyFPSRenderer:

    def update(self):
        pass

    def render(self):
        pass

class SharedVariablesRenderer:

    @dataclass
    class State:
        name: str
        value: Any
        surface: pygame.Surface
        rect: pygame.Rect

    def __init__(self, engine):
        self.engine = engine
        self._states = OrderedDict()

    def render(self, shared_variables):
        if shared_variables.has_changed:
            self._update(shared_variables)
            shared_variables.clear_change_flag()
        for state in self._states.values():
            self.engine.scene.surface.fill(Color.black._c, state.rect)
            self.engine.scene.surface.blit(state.surface, state.rect)

    def _update(self, shared_variables):
        update_rect = False
        for name in shared_variables:
            var = shared_variables[name]
            state = self._states.get(name, None)
            if var._visible:
                if state is None:
                    state = self.State(name=name, value=None,
                                       surface=None, rect=None)
                    self._states[name] = state
                    update_rect = True
                else:
                    pass
                if state.value != var.get():
                    state.value = var.get()
                    state.surface = self.engine.default_font.render(
                        f"{state.name} = {state.value}", True, Color.white._c)
                    if state.rect is not None:
                        state.rect.width = state.surface.get_rect().width
                        assert state.rect.height == state.surface.get_rect().height
            else:
                if state is None:
                    pass
                else:
                    del self._states[name]
                    update_rect = True
        if update_rect:
            top = 0
            for state in self._states.values():
                state.rect = state.surface.get_rect().copy()
                state.rect.top = top
                top += state.rect.height

class Renderer:

    def __init__(self, engine, show_fps=False):
        self.engine = engine
        self.fps = FrequencyMeter()
        self._fps_renderer = FPSRenderer(self.fps, engine) if show_fps else DummyFPSRenderer()
        self._shared_variables_renderer = SharedVariablesRenderer(self.engine)

    def render(self):
        self._render_scene(self.engine.scene)
        self._render_sprites(self.engine.scene, self.engine.sprites)
        self._shared_variables_renderer.render(self.engine.shared_variables)
        if self.fps.update():
            self._fps_renderer.update()
        self._fps_renderer.render()
        self.engine._flip()

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

class Server:

    def __init__(self, engine):
        self.engine = engine
        self._running = [] # currently running processors

    def process_requests(self):
        self._collect()
        self._run()

    def _collect(self):
        for script in self.engine.scripts:
            try:
                request = script.pipe.request_queue.get(block=False)
            except EmptyQueue:
                pass
            else:
                processor = RequestProcessors.new(self.engine, script, request)
                self._running.append(processor)

    def _run(self):
        still_running = []
        for proc in self._running:
            proc()
            if proc.is_finished:
                proc.script.pipe.reply_queue.put(proc.reply, block=False)
            else:
                still_running.append(proc)
        self._running = still_running

class RequestProcessors:

    @classmethod
    def get(cls, request):
        request_type_name = type(request).__name__
        try:
            return getattr(cls, f"{request_type_name}Processor")
        except AttributeError:
            raise ValueError(
                f"no processor available for request: '{request_type_name}'")

    @classmethod
    def new(cls, engine, script, request):
        proc_type = cls.get(request)
        return proc_type(engine, script, request)

    class RequestProcessor(ABC):
        """Base class of request processor"""

        def __init__(self, engine, script, request):
            self.engine = engine
            self.script = script
            self.request = request
            self._finished = False
            self._reply = None

        def __call__(self):
            try:
                self._run()
            except Exception as e:
                self._finished = True
                self._reply = e

        @property
        def is_finished(self):
            return self._finished

        @property
        def reply(self):
            return self._reply

        @abstractmethod
        def _run(self):
            pass

    class OneShotProcessor(RequestProcessor):
        """Base class of all processor that does not live across multiple frame.
        """

        def _run(self):
            self._reply = self._run_once()
            self._finished = True

        @abstractmethod
        def _run_once(self):
            pass

    class SharedVariableNewProcessor(OneShotProcessor):
        def _run_once(self):
            self.engine.shared_variables[self.request.name] = self.request.value

    class SharedVariableDelProcessor(OneShotProcessor):
        def _run_once(self):
            del self.engine.shared_variables[self.request.name]

    class SharedVariableOpProcessor(OneShotProcessor):
        def _run_once(self):
            f = getattr(self.engine.shared_variables[self.request.name],
                        self.request.op)
            return f(*self.request.args, **self.request.kwargs)

    class BackdropSwitchToProcessor(OneShotProcessor):
        def _run_once(self):
            if self.engine.scene.backdrop != self.request.name:
                try:
                    self.engine.scene.backdrop = self.request.name
                except KeyError:
                    raise ValueError(f"invalid backdrop: '{self.request.name}'")
                self.engine.event_manager.schedule(
                    event.BackdropSwitches(backdrop=self.request.name))

    class SpriteOpProcessor(OneShotProcessor):
        def _run_once(self):
            sprite = self.engine.sprites[self.request.name]
            f = getattr(sprite, self.request.op)
            return f(*self.request.args, **self.request.kwargs)

    class SpriteBatchOpProcessor(OneShotProcessor):
        def _run_once(self):
            sprite = self.engine.sprites[self.request.name]
            rets = []
            for op in self.request.ops:
                f = getattr(sprite, op["op"])
                ret = f(*op.get("args", ()), **op.get("kwargs", {}))
                rets.append(ret)
            return rets

    class SpriteGetCollisionProcessor(OneShotProcessor):
        # TODO(Nicolas Despres): Handle mask
        def _run_once(self):
            sprite = self.engine.sprites[self.request.name]
            collisions = []
            if not self.engine.scene.rect.contains(sprite.rect):
                collisions.append(SCENE_EDGE)
            for name, other_sprite in self.engine.sprites.items():
                if sprite.rect.colliderect(other_sprite.rect):
                    collisions.append(name)
            return collisions

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

class EventManager:

    def __init__(self, engine):
        self.engine = engine
        self.event_handlers = event.EventHandlers()
        self._pending = []

    def schedule(self, event):
        handlers = self.event_handlers.get(event)
        # print(f"schedule {len(handlers)} handlers for event: {event} - hash_value={event._hash_value!r} - hash={hash(event)}")
        self._pending.extend(handlers)

    def trigger(self):
        # if self._pending:
        #     print(f"trigger")
        self.engine.scripts.bulk_trigger(self._pending)
        self._pending.clear()

    def check(self):
        for e in self.event_handlers:
            try:
                self._check_event(e)
            except Exception as exc:
                raise ValueError(f"{exc} in event handlers: {', '.join(h.name for h in self.event_handlers.get(e))}")

    def _check_event(self, e):
        if isinstance(e, event.BackdropSwitches):
            if e.backdrop not in self.engine.scene.backdrops:
                raise ValueError(f"unknown backdrop '{e.backdrop}'")
        elif isinstance(e, event.KeyPressed):
            check_key(e.key)

class Engine:

    def __init__(self, project, show_fps=False):
        self.project = project
        self.scene = _Scene()
        self.sprites = {}
        self._is_running = False
        self.event_manager = EventManager(self)
        self.scripts = ScriptSet()
        self.shared_variables = SharedVariableSet()
        self._renderer = Renderer(self, show_fps=show_fps)

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
            self.scene.surface = pygame.display.set_mode(self.scene.size)
            pygame.key.set_repeat(300, # ms
                                  30) # ms
            self._load()
            self.event_manager.check()
            self._configure()
            self.scripts.scene = Scene.from_scene(self.scene)
            self._server = Server(self)
            return self._loop()
        finally:
            self._is_running = False
            pygame.quit()

    def _flip(self):
        pygame.display.flip()

    LOAD_BACK_COLOR = Color(62, 254, 165)

    def _load(self):
        # print("Loading font")
        default_font_name = pygame.font.get_default_font()
        # print(f"default font: {default_font_name}")
        self.default_font = pygame.font.Font(default_font_name, 16)
        print("Loading...")
        self.scene.surface.fill(self.LOAD_BACK_COLOR._c)
        self._flip()
        Loader(progress=ConsoleProgress()).load(self)

    def _configure(self):
        print("Configuring...")
        Configurer(self).configure()

    def _loop(self):
        self.event_manager.schedule(event.ProgramStart())
        loop = FixedDeltaTimeEngineLoop(self._render, self._simulate, 100)
        clock = pygame.time.Clock()
        while self._is_running:
            loop.step()
        self.scripts.join()

    def _simulate(self):
        self.event_manager.trigger()
        self._process_user_input()
        self._server.process_requests()
        self.scripts.rip_done_scripts()

    def _render(self):
        self._renderer.render()

    def _process_user_input(self):
        for e in pygame.event.get():
            # print(type(event), event)
            if e.type == pygame.QUIT:
                self._is_running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self._is_running = False
                else:
                    for k in iter_keys():
                        if e.key in k.code:
                            self.event_manager.schedule(
                                event.KeyPressed(key=k.name))
            # elif event.type == pygame.MOUSEMOTION:
            #     MOUSE._set_pos(*event.pos)
