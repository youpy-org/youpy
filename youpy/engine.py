# -*- encoding: utf-8 -*-
"""
"""


from collections.abc import MutableMapping
from collections import OrderedDict
from collections import Counter
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from time import time

import pygame

from youpy.project import Project
from youpy.tools import FrequencyMeter
from youpy.tools import print_simple_banner
from youpy.tools import format_milliseconds
from youpy.data import Color
from youpy.data import EngineScene
from youpy import event
from youpy.loader import Loader
from youpy.configurer import Configurer
from youpy.script import ScriptSet
from youpy.script import set_scene
from youpy import message
from youpy.concurrency import EmptyQueue
from youpy.keys import iter_keys
from youpy.keys import check_key


from youpy import logging
LOGGER = logging.getLogger(__name__)


class ConsoleProgress:

    def in_section(self, name, index, path):
        print(f"\ro {name:10s} : {index+1: 4d}", end="")

    def end_section(self):
        print() # flush

class LoggerProgress:

    def __init__(self):
        self._count = Counter()

    def in_section(self, name, index, path):
        self._count[name] += 1
        LOGGER.info(f"Loading {index+1: 4d}th {name:>10s}: {path}")

    def end_section(self):
        for name, count in self._count.items():
            LOGGER.info(f"Loaded {count} {name}(s)")
        # Reset counter between each section, otherwise previous section count
        # are repeated.
        self._count.clear()

class FPSRenderer:

    def __init__(self, fps, simu):
        self.fps = fps
        self.simu = simu

    def update(self):
        self._surf = self.simu.default_font.render(
            f'{self.fps.frequency: 3.0f}', True, Color.white._c)
        self._rect = self._surf.get_rect().copy()
        self._rect.topleft = (self.simu.scene.width - self._rect.width, 0)
        print("FPS:", self.fps)

    def render(self):
        self.simu.scene.surface.fill(Color.black._c, self._rect)
        self.simu.scene.surface.blit(self._surf, self._rect)

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

    def __init__(self, simu):
        self.simu = simu
        self._states = OrderedDict()

    def render(self, shared_variables):
        if shared_variables.has_changed:
            self._update(shared_variables)
            shared_variables.clear_change_flag()
        for state in self._states.values():
            self.simu.scene.surface.fill(Color.black._c, state.rect)
            self.simu.scene.surface.blit(state.surface, state.rect)

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
                    state.surface = self.simu.default_font.render(
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

    def __init__(self, simu, show_fps=False):
        self.simu = simu
        self.fps = FrequencyMeter()
        self._fps_renderer = FPSRenderer(self.fps, simu) if show_fps else DummyFPSRenderer()
        self._shared_variables_renderer = SharedVariablesRenderer(self.simu)

    def render(self):
        self._render_scene(self.simu.scene)
        self._render_sprites(self.simu.scene, self.simu.sprites)
        self._shared_variables_renderer.render(self.simu.shared_variables)
        if self.fps.update():
            self._fps_renderer.update()
        self._fps_renderer.render()

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

    def __init__(self, simu):
        self.simu = simu
        self._running = [] # currently running processors

    def process_requests(self):
        self._collect()
        self._run()

    def _collect(self):
        for script in self.simu.scripts:
            try:
                request = script.pipe.request_queue.get(block=False)
            except EmptyQueue:
                pass
            else:
                processor = RequestProcessors.new(self.simu, script, request)
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
    def new(cls, simu, script, request):
        proc_type = cls.get(request)
        return proc_type(simu, script, request)

    class RequestProcessor(ABC):
        """Base class of request processor"""

        def __init__(self, simu, script, request):
            self.simu = simu
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
            self.simu.shared_variables[self.request.name] = self.request.value

    class SharedVariableDelProcessor(OneShotProcessor):
        def _run_once(self):
            del self.simu.shared_variables[self.request.name]

    class SharedVariableOpProcessor(OneShotProcessor):
        def _run_once(self):
            f = getattr(self.simu.shared_variables[self.request.name],
                        self.request.op)
            return f(*self.request.args, **self.request.kwargs)

    class BackdropSwitchToProcessor(OneShotProcessor):
        def _run_once(self):
            if self.simu.scene.backdrop != self.request.name:
                try:
                    self.simu.scene.backdrop = self.request.name
                except KeyError:
                    raise ValueError(f"invalid backdrop: '{self.request.name}'")
                self.simu.event_manager.schedule(
                    event.BackdropSwitches(backdrop=self.request.name))

    class SpriteOpProcessor(OneShotProcessor):
        def _run_once(self):
            sprite = self.simu.sprites[self.request.name]
            f = getattr(sprite, self.request.op)
            return f(*self.request.args, **self.request.kwargs)

    class SpriteBatchOpProcessor(OneShotProcessor):
        def _run_once(self):
            sprite = self.simu.sprites[self.request.name]
            rets = []
            for op in self.request.ops:
                f = getattr(sprite, op["op"])
                ret = f(*op.get("args", ()), **op.get("kwargs", {}))
                rets.append(ret)
            return rets

    class SpriteGetCollisionProcessor(OneShotProcessor):
        # TODO(Nicolas Despres): Handle mask
        def _run_once(self):
            sprite = self.simu.sprites[self.request.name]
            collisions = []
            if not self.simu.scene.rect.contains(sprite.rect):
                collisions.append(EngineScene.EDGE)
            for name, other_sprite in self.simu.sprites.items():
                if sprite.rect.colliderect(other_sprite.rect):
                    collisions.append(name)
            return collisions

    class WaitProcessor(RequestProcessor):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_time = self.simu.elapsed_time

        def _run(self):
            self._finished = (self.simu.elapsed_time - self.start_time > self.request.delay)

    class StopProgramProcessor(OneShotProcessor):
        def _run_once(self):
            LOGGER.info(f"script {self.script.name} has stopped the program")
            self.simu.stop(reason=self.request.reason)

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

    def __init__(self, simu):
        self.simu = simu
        self.event_handlers = event.EventHandlers()
        self._pending = []

    def schedule(self, event):
        handlers = self.event_handlers.get(event)
        #LOGGER.debug(f"schedule {len(handlers)} handlers for event: {event} - hash_value={event._hash_value!r}")
        self._pending.extend(handlers)

    def trigger(self):
        # if self._pending:
        #     print(f"trigger")
        self.simu.scripts.bulk_trigger(self._pending)
        self._pending.clear()

    def check(self):
        for e in self.event_handlers:
            try:
                self._check_event(e)
            except Exception as exc:
                raise ValueError(f"{exc} in event handlers: {', '.join(h.name for h in self.event_handlers.get(e))}")

    def _check_event(self, e):
        if isinstance(e, event.BackdropSwitches):
            if e.backdrop not in self.simu.scene.backdrops:
                raise ValueError(f"unknown backdrop '{e.backdrop}'")
        elif isinstance(e, event.KeyPressed):
            check_key(e.key)

class AbstractSimulation(ABC):

    def __init__(self):
        self.__is_running = False
        # Total simulated time elapsed since the simulation boot
        self.__time = 0
        self.__real_simu_duration = 0
        self.__real_render_duration = 0

    @property
    def is_running(self):
        return self.__is_running

    def stop(self, reason=""):
        """Request the simulation to stop."""
        self.__is_running = False
        if reason:
            LOGGER.info(f'Program stop because "{reason}"')

    @property
    def time(self):
        return self.__time

    def boot(self):
        if self.__is_running:
            raise RuntimeError("simulation already running")
        self.__is_running = True
        self._on_boot()

    @abstractmethod
    def _on_boot(self):
        pass

    def shutdown(self):
        """Shut everything down (opposite of boot)."""
        if self.__is_running:
            raise RuntimeError("simulation still running")
        self._on_shutdown()

    @abstractmethod
    def _on_shutdown(self):
        pass

    def halt(self):
        """Always called."""
        self.__is_running = False
        self._on_halt()

    @abstractmethod
    def _on_halt(self):
        pass

    def flip(self):
        self._on_flip()

    @abstractmethod
    def _on_flip(self):
        pass

    def simulate(self, delta_time):
        t0 = time()
        self._on_simulate(delta_time)
        t1 = time()
        self.__real_simu_duration = int((t1 - t0) * 1000)
        if self.__real_simu_duration > delta_time:
            LOGGER.warning(f"it tooks {self.__real_simu_duration}ms to simulate {delta_time}ms: simulation is too slow!")
        self.__time += delta_time

    @property
    def real_simu_duration(self):
        return self.__real_simu_duration

    @abstractmethod
    def _on_simulate(self, delta_time):
        pass

    def render(self):
        t0 = time()
        self._on_render()
        t1 = time()
        self.__real_render_duration = int((t1 - t0) * 1000)

    @property
    def real_render_duration(self):
        return self.__real_render_duration

    @abstractmethod
    def _on_render(self):
        pass

class Simulation(AbstractSimulation):

    def __init__(self, project, show_fps=False):
        super().__init__()
        self.project = project
        self.scene = EngineScene()
        self.sprites = {}
        self.event_manager = EventManager(self)
        self.scripts = ScriptSet()
        self.shared_variables = SharedVariableSet()
        self._renderer = Renderer(self, show_fps=show_fps)

    def _on_boot(self):
        self._show_banner()
        pygame.init()
        pygame.display.set_caption(self.project.name)
        self.scene.surface = pygame.display.set_mode(self.scene.size)
        pygame.key.set_repeat(300, # ms
                              30) # ms
        self._load()
        self.event_manager.check()
        self._configure()
        set_scene(self.scene)
        self._server = Server(self)
        self.event_manager.schedule(event.ProgramStart())

    def _on_shutdown(self):
        self.scripts.join()

    def _on_halt(self):
        pygame.quit()

    def _on_flip(self):
        pygame.display.flip()

    def _show_banner(self):
        def printer(msg):
            LOGGER.log(logging.PRINT, msg)
        print_simple_banner(f"Initializing {self.project.name}...",
                            separator="*",
                            printer=printer)


    LOAD_BACK_COLOR = Color(62, 254, 165)

    def _load(self):
        # print("Loading font")
        default_font_name = pygame.font.get_default_font()
        # print(f"default font: {default_font_name}")
        self.default_font = pygame.font.Font(default_font_name, 16)
        LOGGER.info("Loading...")
        self.scene.surface.fill(self.LOAD_BACK_COLOR._c)
        self.flip()
        Loader(progress=LoggerProgress()).load(self)

    def _configure(self):
        LOGGER.info("Configuring...")
        Configurer(self).configure()

    def _on_simulate(self, delta_time):
        self.event_manager.trigger()
        self._process_user_input()
        self._server.process_requests()
        self.scripts.rip_done_scripts()

    def _on_render(self):
        self._renderer.render()

    def _process_user_input(self):
        for e in pygame.event.get():
            # print(type(event), event)
            if e.type == pygame.QUIT:
                self.stop(reason="window was closed")
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.stop(reason="escape was pressed")
                else:
                    for k in iter_keys():
                        if e.key in k.code:
                            self.event_manager.schedule(
                                event.KeyPressed(key=k.name))
            # elif event.type == pygame.MOUSEMOTION:
            #     MOUSE._set_pos(*event.pos)

class Engine:
    """Run a simulation.

    Parameters:
      target_fps: the number of frames per second the engine will try to run at
      delta_time: one physical time step in millisecond
    """

    def __init__(self, simu, target_fps=30, delta_time=5):
        if not isinstance(target_fps, int):
            raise TypeError("target_fps must be int, not {}"
                            .format(type(target_fps).__name__))
        if not isinstance(delta_time, int):
            raise TypeError("delta_time must be int, not {}"
                            .format(type(delta_time).__name__))
        self.simu = simu
        self._target_fps = target_fps # The pace will try to keep
        self._delta_time = delta_time
        # Initialized in run() after the simulation boot
        self._clock = None

    @property
    def is_running(self):
        return self.simu.is_running

    def run(self):
        try:
            self.simu.boot()
            self._clock = pygame.time.Clock()
            # Total running time (physics+rendering+sleep)
            # elapsed since the simulation boot
            self._running_time = 0
            self._started_at = time()
            accumulated_time = 0
            while self.simu.is_running:
                frame_time = self._clock.get_time()
                self._running_time += frame_time
                accumulated_time += frame_time
                simu_count = 0
                while accumulated_time >= self._delta_time:
                    self.simu.simulate(self._delta_time)
                    accumulated_time -= self._delta_time
                    simu_count += 1
                self.simu.render()
                # slowdown the simulation to meet the target FPS
                self._clock.tick_busy_loop(self._target_fps)
                self.simu.flip()
                # print(f"FPS={self.fps:.2f} ; {simu_count=} ; {frame_time=} ; simu={format_milliseconds(self.simu.time)} ; running={format_milliseconds(self._running_time)} ; simu_duration={self.simu.real_simu_duration}ms ; render_duration={self.simu.real_render_duration}ms ; real={format_milliseconds(self.real_time)}")
            self.simu.shutdown()
        finally:
            self.simu.halt()

    @property
    def elapsed_time(self):
        return self._clock.get_time()

    @property
    def target_fps(self):
        return self._target_fps

    @property
    def delta_time(self):
        return self._delta_time

    @property
    def running_time(self):
        return self._running_time

    @property
    def real_time(self):
        return int((time() - self._started_at) * 1000) # ms

    @property
    def fps(self):
        return self._clock.get_fps()
