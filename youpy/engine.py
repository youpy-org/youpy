# -*- encoding: utf-8 -*-
"""
"""


from collections import OrderedDict
from collections import Counter
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from time import time
from time import sleep

import pygame

from youpy.project import Project
from youpy.tools import FrequencyMeter
from youpy.tools import print_simple_banner
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
from youpy import math
from youpy.shared_variables import SharedVariableSet
from youpy import physics


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
            if proc.is_finished:
                proc.script.pipe.reply_queue.put(proc.reply, block=False)
            else:
                proc()
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
            self.__finished = False
            self.__reply = None

        def __call__(self):
            try:
                self._run()
            except Exception as e:
                self._set_reply(e)

        @property
        def is_finished(self):
            return self.__finished

        @property
        def reply(self):
            return self.__reply

        def _set_reply(self, reply):
            self.__reply = reply
            self.__finished = True

        def _set_reply_if(self, condition, reply=None):
            if condition:
                self._set_reply(reply)

        @abstractmethod
        def _run(self):
            pass

    class OneShotProcessor(RequestProcessor):
        """Base class of all processor that does not live across multiple frame.
        """

        def _run(self):
            self._set_reply(self._run_once())

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

    class SpriteMoveProcessor(RequestProcessor):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            sprite = self.simu.sprites[self.request.name]
            self.system = SpriteMoveSystem(sprite, self.request.step)
            self.simu._physical_engine.schedule(self.system)

        def _run(self):
            self._set_reply_if(self.system.is_finished)

    class WaitProcessor(RequestProcessor):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_time = self.simu.time

        def _run(self):
            waiting_time = self.simu.time - self.start_time
            self._set_reply_if(waiting_time > self.request.delay)

    class StopProgramProcessor(OneShotProcessor):
        def _run_once(self):
            self.simu.stop(reason=self.request.reason)

class SpriteMoveSystem(physics.PhysicalSystem):

    def __init__(self, sprite, move_step):
        super().__init__()
        self.sprite = sprite
        self.move_step = move_step

    def _on_start(self):
        if self.move_step == 0:
            self._set_result(None)
            return
        self.step_count = math.floor(self.sprite.MOVE_DURATION / self.engine.delta_time)
        assert self.step_count > 0, "MOVE_DURATION must be higher than simulation delta-time"
        self.velocity = self.sprite.get_velocity_from_direction()
        assert math.isclose(self.velocity.norm(), 1.0)
        self.final = self.sprite.position + self.move_step * self.velocity
        inc_step = self.move_step / self.step_count
        self.velocity *= inc_step

    def _on_step(self):
        self.sprite.move_by_velocity(self.velocity)
        self.step_count -= 1
        if self.step_count == 0:
            self._finish()

    def _finish(self):
        # Move the sprite to the final position in all cases so that
        # if MOVE_DURATION is not a multiple of delta_time, we still end-up
        # at the right position.
        self.sprite.go_to_position(self.final)
        self._set_result_if(self.step_count == 0)

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

class FPS:

    def __init__(self, window_size=20):
        self._window_size = window_size
        self._tick = time()
        self._count = 0
        self._fps = 0

    def tick(self):
        self._count += 1
        if self._count >= self._window_size:
            t = time()
            duration = t - self._tick
            self._fps = self._count / duration
            self._count = 0
            self._tick = t

    @property
    def fps(self):
        return self._fps

class AbstractSimulation(ABC):

    def __init__(self):
        self.__is_running = False
        self.__real_simu_duration = 0
        self.__real_render_duration = 0
        self.fps = FPS()

    @property
    @abstractmethod
    def delta_time(self):
        pass

    @property
    def is_running(self):
        return self.__is_running

    def stop(self, reason=""):
        """Request the simulation to stop."""
        self.__is_running = False
        if reason:
            LOGGER.info(f'Program stop because "{reason}"')

    @property
    @abstractmethod
    def time(self):
        """Return the total simulated time (in seconds) elapsed since the simulation boot."""
        pass

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

    def process_inputs(self):
        self._on_process_inputs()

    def simulate(self):
        t0 = time()
        self._on_simulate()
        t1 = time()
        self.__real_simu_duration = t1 - t0
        if self.__real_simu_duration > self.delta_time:
            LOGGER.warning(f"it tooks {self.__real_simu_duration}s to simulate {self.delta_time}s: simulation is too slow!")

    @property
    def real_simu_duration(self):
        return self.__real_simu_duration

    @abstractmethod
    def _on_simulate(self):
        pass

    def render(self):
        t0 = time()
        self._on_render()
        t1 = time()
        self.fps.tick()
        self.__real_render_duration = t1 - t0

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
        self._physical_engine = physics.PhysicalEngine()
        self._renderer = Renderer(self, show_fps=show_fps)

    @property
    def delta_time(self):
        return self._physical_engine.delta_time

    @property
    def time(self):
        return self._physical_engine.time

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

    def _on_process_inputs(self):
        self.event_manager.trigger()
        self._process_user_input()
        self._server.process_requests()
        self.scripts.rip_done_scripts()

    def _on_simulate(self):
        self._physical_engine.step()

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
    """

    def __init__(self, simu, target_fps=30):
        if not isinstance(target_fps, int):
            raise TypeError("target_fps must be int, not {}"
                            .format(type(target_fps).__name__))
        self.simu = simu
        if self.simu.delta_time > 1 / target_fps:
            LOGGER.warning(f"simulation delta-time {self.simu.delta_time}ms is larger than target FPS={target_fps}: simulation will never catch up")
        self._target_fps = target_fps # The pace will try to keep
        # Initialized in run() after the simulation boot
        self._clock = None

    @property
    def is_running(self):
        return self.simu.is_running

    def run(self):
        try:
            self.simu.boot()
            # Total running time (physics+rendering+sleep)
            # elapsed since the simulation boot
            self._running_time = 0
            self.epoch = time()
            accumulated_time = 0
            target_frame_time = 1 / self.target_fps
            frame_time = 0
            while self.simu.is_running:
                tick0 = time()
                accumulated_time += frame_time
                simu_count = 0
                while accumulated_time >= self.simu.delta_time:
                    self.simu.process_inputs()
                    self.simu.simulate()
                    # Give a chance to the OS to schedule the user thread.
                    sleep(1e-6)
                    accumulated_time -= self.simu.delta_time
                    simu_count += 1
                self.simu.render()
                self.simu.flip()
                tick = time()
                # Process inputs with the remaining time until we reach the
                # target_frame_time
                while tick - tick0 <= target_frame_time:
                    self.simu.process_inputs()
                    # Give a chance to the OS to schedule the user thread.
                    sleep(1e-6)
                    tick = time()
                frame_time = tick - tick0
                LOGGER.debug(f"FPS={self.fps:.2f} ; {simu_count=} ; {frame_time=:.6f}s ; {accumulated_time=:.6f}s ; simu={self.simu.time:.6f}s ; running={self._running_time:.6f}s ; simu_duration={self.simu.real_simu_duration:.6f}s ; render_duration={self.simu.real_render_duration:.6f}s ; real={self.real_time:.6f}")
                self._running_time += frame_time
            self.simu.shutdown()
        finally:
            self.simu.halt()

    @property
    def target_fps(self):
        return self._target_fps

    @property
    def running_time(self):
        return self._running_time

    @property
    def real_time(self):
        return time() - self.epoch # sec

    @property
    def fps(self):
        return self.simu.fps.fps
