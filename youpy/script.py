# -*- encoding: utf-8 -*-
"""
"""


import sys
import traceback

from youpy import concurrency
from youpy import message
from youpy.logging import get_user_logger_name
from youpy.logging import getLogger
from inspect import signature
from youpy.data import EngineSprite
from youpy.data import EngineScene

LOGGER = getLogger(__name__)

class ScriptSet:

    def __init__(self):
        self._scripts = {}
        self._done_scripts = concurrency.Queue()

    def bulk_trigger(self, event_handlers):
        for event_handler in event_handlers:
            self.trigger(event_handler)

    def trigger(self, event_handler):
        script_name = get_script_name(event_handler)
        if script_name in self._scripts:
            # Script already running. This may happens for example when the
            # event handler run slower than the pace of repeated key stroke.
            # In such a case, we just drop some event.
            return
        script = Script(event_handler, done_queue=self._done_scripts)
        self._scripts[script.name] = script
        script.start()

    def rip_done_scripts(self):
        while True:
            try:
                script = self._done_scripts.get(block=False)
            except concurrency.EmptyQueue:
                break
            else:
                del self._scripts[script.name]
                if script.exc_info is not None:
                    print(f"*** Exception in thread {script.name}")
                    traceback.print_exception(*script.exc_info)

    def join(self, timeout=1.0):
        self._stop_all_scripts()
        terminated = []
        for s in self._scripts.values():
            s.join(timeout=timeout)
            if not s.is_alive():
                terminated.append(s.name)
        for name in terminated:
            del self._scripts[name]
        if self._scripts:
            LOGGER.error(f"There were {len(self._scripts)} non-terminated scripts:")
            for name in self._scripts:
                LOGGER.error(f"  {name}")
            return False
        return True

    def _stop_all_scripts(self):
        for script in self._scripts.values():
            script.pipe.reply_queue.put(StopScript())

    def __iter__(self):
        return iter(self._scripts.values())

    def __len__(self):
        return len(self._scripts)

class StopScript(Exception):
    pass

def get_script_name(event_handler):
    return event_handler.name

class Script(concurrency.Task):

    context = concurrency.get_context()

    def __init__(self, event_handler, done_queue=None):
        super().__init__(name=get_script_name(event_handler), daemon=True)
        self.event_handler = event_handler
        self.pipe = concurrency.Pipe()
        self._done_queue = done_queue
        self.exc_info = None

    def run(self):
        self.context.script = self
        if self.event_handler.sprite is not None:
            self.context.frontend_sprite = Sprite(self.event_handler.sprite)
        try:
            self._run()
        except StopScript:
            pass
        except Exception as exc:
            self.exc_info = sys.exc_info()
        finally:
            if self._done_queue is not None:
                self._done_queue.put(self, block=False)

    def _run(self):
        if self.event_handler.in_stage:
            return self.event_handler.callback()
        else:
            sig = signature(self.event_handler.callback)
            nparameters = len(sig.parameters)
            if nparameters == 0:
                return self.event_handler.callback()
            elif nparameters == 1:
                return self.event_handler.callback(self.context.frontend_sprite)
            else:
                raise TypeError(f"too many parameters defined for event handler '{self.event_handler_name}'")

    def send(self, request):
        self.pipe.request_queue.put(request)
        reply = self.pipe.reply_queue.get()
        if isinstance(reply, Exception):
            raise reply
        return reply

# ====================
# Front-end Sprite API
# ====================

def get_context_script():
    """Return the script bound to the current thread."""
    return Script.context.script

def send_request(request):
    """Send a request to the engine server."""
    return get_context_script().send(request)


class Scene:
    """Scene holds properties of the stage.
    """

    # WARNING: Make sure everything is read-only since they are accessed
    #          concurrently.

    __slots__ = ("_engine_scene",)

    def __init__(self, engine_scene):
        if not isinstance(engine_scene, EngineScene):
            raise TypeError("EngineScene must be scene, not {}"
                            .format(type(EngineScene).__name__))
        self._engine_scene = engine_scene

    @property
    def width(self):
        return self._engine_scene.width

    @property
    def height(self):
        return self._engine_scene.height

    @property
    def edge(self):
        return self._engine_scene.EDGE

_SCENE = None

def set_scene(engine_scene):
    # Must be called before the game start and never changed during to
    # prevent data collision when accessed concurrently.
    global _SCENE
    _SCENE = Scene(engine_scene)

def get_scene():
    return _SCENE

def get_script_logger_name():
    script = get_context_script()
    name = get_script_name(script.event_handler)
    return get_user_logger_name(name)

def get_script_logger():
    return getLogger(get_script_logger_name())

def get_context_frontend_sprite():
    return Script.context.frontend_sprite

from youpy import math # needed by bounce

class Sprite:

    def __init__(self, engine_sprite):
        if not isinstance(engine_sprite, EngineSprite):
            raise TypeError("engine_sprite must be EngineSprite, not {}"
                            .format(type(engine_sprite).__name__))
        self._engine_sprite = engine_sprite

    @property
    def name(self):
        return self._engine_sprite.name

    @property
    def _scene(self):
        return self._engine_sprite.scene

    def go_to(self, x, y):
        """Change sprite position to _x_ and _y_."""
        if not isinstance(x, int):
            raise TypeError("x must be int, not {}"
                            .format(type(x).__name__))
        if not isinstance(y, int):
            raise TypeError("y must be int, not {}"
                            .format(type(y).__name__))
        send_request(message.SpriteOp(
            name=self.name,
            op="go_to",
            args=self._scene.coordsys.point_from(x, y)))

    def set_x_to(self, x):
        if not isinstance(x, int):
            raise TypeError("x must be int, not {}"
                            .format(type(x).__name__))
        send_request(message.SpriteOp(
            name=self.name,
            op="go_to",
            args=(self._scene.coordsys.abscissa_from(x), None)))

    def set_y_to(self, y):
        if not isinstance(y, int):
            raise TypeError("y must be int, not {}"
                            .format(type(y).__name__))
        send_request(message.SpriteOp(
            name=self.name,
            op="go_to",
            args=(None, self._scene.coordsys.ordinate_from(y))))

    def move_by(self, step_x, step_y):
        """Change sprite position by _step_x_ and _step_y_."""
        if not isinstance(step_x, int):
            raise TypeError("step_x must be int, not {}"
                            .format(type(step_x).__name__))
        if not isinstance(step_y, int):
            raise TypeError("step_y must be int, not {}"
                            .format(type(step_y).__name__))
        send_request(message.SpriteOp(
            name=self.name,
            op="move_by",
            args=(self._scene.coordsys.dir_x * step_x,
                  self._scene.coordsys.dir_y * step_y)))

    def change_x_by(self, step_x):
        if not isinstance(step_x, int):
            raise TypeError("step_x must be int, not {}"
                            .format(type(step_x).__name__))
        send_request(message.SpriteOp(
            name=self.name,
            op="move_by",
            args=(self._scene.coordsys.dir_x * step_x, 0)))

    def change_y_by(self, step_y):
        if not isinstance(step_y, int):
            raise TypeError("step_y must be int, not {}"
                            .format(type(step_y).__name__))
        send_request(message.SpriteOp(
            name=self.name,
            op="move_by",
            args=(0, self._scene.coordsys.dir_y * step_y)))

    def point_in_direction(self, angle):
        send_request(message.SpriteOp(
            name=self.name,
            op="point_in_direction",
            args=(self._scene.anglesys.to_degree(angle),)))

    def move(self, step):
        send_request(message.SpriteOp(
            name=self.name,
            op="move",
            args=(step,)))

    def _get_state(self):
        return send_request(message.SpriteOp(name=self.name, op="get_state"))

    def position(self):
        return self._scene.coordsys.point_to(*self._get_state().position())

    def x_position(self):
        return self.position()[0]

    def y_position(self):
        return self.position()[1]

    def direction(self):
        return self._scene.anglesys.from_degree(self._get_state().direction())

    def bounce_if_on_edge(self):
        st = self._get_state()
        angle_degree = st.direction()
        r = st.rect
        scene = self._scene
        if r.left < 0 or r.right > scene.width: # vertical edges
            new_angle = math.atan2(math.fast_sin(angle_degree),
                                   -math.fast_cos(angle_degree))
            if r.left < 0:
                dx = -r.left
            else:
                dx = scene.width - r.right
            dy = int(round(dx * math.tan(new_angle)))
        elif r.top < 0 or r.bottom > scene.height: # horizontal edges
            new_angle = math.atan2(-math.fast_sin(angle_degree),
                                   math.fast_cos(angle_degree))
            if r.top < 0:
                dy = r.top
            else:
                dy = r.bottom - scene.height
            dx = int(round(dy * math.tan(new_angle)))
        else: # no collision
            return
        new_angle_degree = int(round(math.radian_to_degree(new_angle))) % 360
        # print(f"{angle_degree=};{new_angle=};{new_angle_degree=};{r=};{dx=};{dy=}")
        send_request(message.SpriteBatchOp(
            name=self.name,
            ops=(
                dict(op="point_in_direction",
                     args=(new_angle_degree,)),
                dict(op="move_by", args=(scene.coordsys.dir_x * dx,
                                         scene.coordsys.dir_y * dy)),
            )))

    def turn_counter_clockwise(self, angle):
        send_request(message.SpriteOp(
            name=self.name,
            op="turn_counter_clockwise",
            args=(angle,)))

    def turn_clockwise(self, angle):
        return self.turn_counter_clockwise(-angle % 360)

    def show(self):
        """Show the current sprite."""
        send_request(message.SpriteOp(name=self.name, op="show"))

    def hide(self):
        """Hide the current sprite."""
        send_request(message.SpriteOp(name=self.name, op="hide"))

    def touched_objects(self):
        return send_request(message.SpriteGetCollision(name=self.name))

    def touching(self, object):
        return object in self.touched_objects()
