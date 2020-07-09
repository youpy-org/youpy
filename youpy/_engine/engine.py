# -*- encoding: utf-8 -*-
"""
"""


from collections.abc import MutableMapping
from collections import OrderedDict

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

    def process_requests(self):
        for script in self.engine.scripts:
            try:
                request = script.pipe.request_queue.get(block=False)
            except EmptyQueue:
                pass
            else:
                try:
                    reply = self.process_request(request)
                except Exception as e:
                    reply = e
                script.pipe.reply_queue.put(reply, block=False)

    def process_request(self, request):
        processor = RequestProcessors.new(self.engine, request)
        return processor()

class RequestProcessors:

    @classmethod
    def get(cls, request):
        request_type_name = type(request).__name__
        if request_type_name == "RequestProcessor":
            raise ValueError("cannot instantiate base request processor")
        try:
            return getattr(cls, f"{request_type_name}Processor")
        except AttributeError:
            raise ValueError(
                f"no processor available for request: '{request_type_name}'")

    @classmethod
    def new(cls, engine, request):
        proc_type = cls.get(request)
        return proc_type(engine, request)

    class RequestProcessor:
        """Base class of request processor"""

        def __init__(self, engine, request):
            self.engine = engine
            self.request = request

    class SharedVariableNewProcessor(RequestProcessor):
        def __call__(self):
            self.engine.shared_variables[self.request.name] = self.request.value

    class SharedVariableDelProcessor(RequestProcessor):
        def __call__(self):
            del self.engine.shared_variables[self.request.name]

    class SharedVariableOpProcessor(RequestProcessor):
        def __call__(self):
            f = getattr(self.engine.shared_variables[self.request.name],
                        self.request.op)
            return f(*self.request.args, **self.request.kwargs)

    class BackdropSwitchToProcessor(RequestProcessor):
        def __call__(self):
            if self.engine.scene.backdrop != self.request.name:
                try:
                    self.engine.scene.backdrop = self.request.name
                except KeyError:
                    raise ValueError(f"invalid backdrop: '{self.request.name}'")
                self.engine.pending_events.extend(self.engine.events.get(events.BackdropSwitches(backdrop=self.request.name)))

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
        self.pending_events = []
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
            self._trigger_pending_events()
            self._render()
        self.scripts.join()

    def _render(self):
        self._renderer.render(self)

    def _trigger_pending_events(self):
        if len(self.pending_events) > 0:
            print(f"trigger {len(self.pending_events)} pending events")
        self.scripts.bulk_trigger(self.pending_events)
        self.pending_events.clear()

_RUNNING_ENGINE = None

def _set_running_engine(engine):
    global _RUNNING_ENGINE
    _RUNNING_ENGINE = engine

def get_running_engine():
    return _RUNNING_ENGINE
