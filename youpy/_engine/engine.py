# -*- encoding: utf-8 -*-
"""
"""


from collections.abc import MutableMapping
from collections import OrderedDict
from abc import ABC
from abc import abstractmethod

import pygame

from youpy._project import Project
from youpy._engine.tools import FrequencyMeter
from youpy._engine.data import Color
from youpy._engine import events
from youpy._engine.loader import Loader
from youpy._engine.configurer import Configurer
from youpy._engine.script import ScriptSet
from youpy._engine import message
from youpy._concurrency import EmptyQueue


class Scene:

    def __init__(self):
        self.width = 480
        self.height = 360
        self.surface = None
        self.backdrops = OrderedDict() # important to support "next backdrop"
        self._backdrop = None

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

    @property
    def backdrop(self):
        return self._backdrop

    @backdrop.setter
    def backdrop(self, backdrop):
        self._backdrop = self.backdrops[backdrop]

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
        next_running = []
        for proc in self._running:
            proc()
            if proc.is_finished:
                proc.script.pipe.reply_queue.put(proc.reply, block=False)
            else:
                next_running.append(proc)
        self._running = next_running

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
            self._run_once()
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
                event = events.BackdropSwitches(backdrop=self.request.name)
                self.engine.trigger(event)

class SharedVariable:

    def __init__(self, value):
        self._value = value
        self._visible = True

    def get(self):
        return self._value

    def hide(self):
        self._visible = False

    def __iadd__(self, other):
        self._value += other

class SharedVariableSet(MutableMapping):

    def __init__(self):
        self._d = {}

    def __setitem__(self, name, value):
        self._d[name] = SharedVariable(value)

    def __getitem__(self, name):
        return self._d[name]

    def __delitem__(self, name):
        del self._d[name]

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

class Engine:

    def __init__(self, project):
        self.project = project
        self.scene = Scene()
        self.sprites = {}
        self._is_running = False
        self.events = events.EventSet()
        self.scripts = ScriptSet()
        self.shared_variables = SharedVariableSet()

    @property
    def is_running(self):
        return self._is_running

    def run(self):
        if self._is_running:
            raise RuntimeError("engine already running")
        self._is_running = True
        _set_running_engine(self)
        try:
            print(f"Initializing {self.project.name}...")
            pygame.init()
            pygame.display.set_caption(self.project.name)
            self.scene.init()
            self._load()
            self._configure()
            self._renderer = Renderer()
            self._server = Server(self)
            return self._loop()
        finally:
            self._is_running = False
            _set_running_engine(None)

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
        self.scripts.bulk_trigger(self.events.iter_all(events.ProgramStart))
        while self._is_running:
            for event in pygame.event.get():
                # print(type(event), event)
                if event.type == pygame.QUIT \
                   or (event.type == pygame.KEYUP
                       and event.key == pygame.K_ESCAPE):
                    self._is_running = False
                # elif event.type == pygame.MOUSEMOTION:
                #     MOUSE._set_pos(*event.pos)
            self._server.process_requests()
            self._render()
        self.scripts.join()

    def _render(self):
        self._renderer.render(self)

    def trigger(self, event):
        self.scripts.bulk_trigger(self.events.get(event))

_RUNNING_ENGINE = None

def _set_running_engine(engine):
    global _RUNNING_ENGINE
    _RUNNING_ENGINE = engine

def get_running_engine():
    return _RUNNING_ENGINE
