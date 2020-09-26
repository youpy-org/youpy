# -*- encoding: utf-8 -*-
"""
"""


import sys
import traceback
from random import randint

from youpy import concurrency
from youpy import message
from youpy.logging import get_user_logger_name
from youpy.logging import getLogger
from inspect import signature
from youpy.data import EngineSprite
from youpy.data import EngineScene
from youpy.data import EngineMouse

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

_MOUSE = None
_SCENE = None

def set_scene(engine_scene):
    # Must be called before the game start and never changed during to
    # prevent data collision when accessed concurrently.
    global _SCENE
    _SCENE = Scene(engine_scene)

def set_mouse(engine_mouse, coordsys):
    # Must be called before the game start and never changed during to
    # prevent data collision when accessed concurrently.
    global _MOUSE
    _MOUSE = Mouse(engine_mouse, coordsys)

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

    @property
    def rect(self):
        r = self._engine_scene.rect
        self._engine_scene.coordsys.set_rect_position(r, Point.null())
        return r

    @property
    def center(self):
        return self.rect.center

    def pick_random_position(self):
        r = self.rect
        return (randint(r.left, r.right), randint(r.top, r.bottom))

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
from youpy.math import Point


# Sprite front-end API
# --------------------
# o Client-side version of the EngineSprite.
# o Parse and check arguments to provide a user-friendly API to users.
# o Do coordinate/angle conversion to honor users preferences.
# Maybe later:
# o Cache local state to reduce engine loads.
class Sprite:
    """A drawn object on stage that can move and collide.
    """

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

    def go_to(self, /, x=None, y=None, point=None):
        """Change sprite position to _x_ and _y_ or to point=(x, y)."""
        if point is None:
            if not isinstance(x, (int, float)):
                raise TypeError("x must be int or float, not {}"
                                .format(type(x).__name__))
            if not isinstance(y, (int, float)):
                raise TypeError("y must be int or float, not {}"
                                .format(type(y).__name__))
        elif isinstance(point, tuple):
            x, y = point
            if not isinstance(x, (int, float)):
                raise TypeError("point first coordinate must be int or float, not {}"
                                .format(type(x).__name__))
            if not isinstance(y, (int, float)):
                raise TypeError("point second coordinate must be int or float, not {}"
                                .format(type(y).__name__))
        else:
            raise TypeError(f"point must be tuple or None, not {type(point).__name__}")
        send_request(message.SpriteMoveTo(
            name=self.name,
            position=self._scene.coordsys.point_from(Point(x, y)).tuple))

    def go_to_sprite(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be str, not {}"
                            .format(type(name).__name__))
        send_request(message.SpriteMoveTo(
            name=self.name,
            position=name))

    def set_x_to(self, x):
        if not isinstance(x, (int, float)):
            raise TypeError("x must be int or float, not {}"
                            .format(type(x).__name__))
        send_request(message.SpriteMoveTo(
            name=self.name,
            position=(self._scene.coordsys.abscissa_from(x), None)))

    def set_y_to(self, y):
        if not isinstance(y, (int, float)):
            raise TypeError("y must be int or float, not {}"
                            .format(type(y).__name__))
        send_request(message.SpriteMoveTo(
            name=self.name,
            position=(None, self._scene.coordsys.ordinate_from(y))))

    def move_by(self, step_x, step_y):
        """Change sprite position by _step_x_ and _step_y_."""
        if not isinstance(step_x, (int, float)):
            raise TypeError("step_x must be int or float, not {}"
                            .format(type(step_x).__name__))
        if not isinstance(step_y, (int, float)):
            raise TypeError("step_y must be int or float, not {}"
                            .format(type(step_y).__name__))
        send_request(message.SpriteMoveBy(
            name=self.name,
            step_by=self._scene.coordsys.vector_from(Point(step_x, step_y))))

    def change_x_by(self, step_x):
        if not isinstance(step_x, (int, float)):
            raise TypeError("step_x must be int or float, not {}"
                            .format(type(step_x).__name__))
        send_request(message.SpriteMoveBy(
            name=self.name,
            step_by=self._scene.coordsys.vector_from(Point(step_x, 0))))

    def change_y_by(self, step_y):
        if not isinstance(step_y, (int, float)):
            raise TypeError("step_y must be int or float, not {}"
                            .format(type(step_y).__name__))
        send_request(message.SpriteMoveBy(
            name=self.name,
            step_by=self._scene.coordsys.vector_from(Point(0, step_y))))

    def point_in_direction(self, angle):
        self._scene.anglesys.check_angle(angle)
        send_request(message.SpriteOp(
            name=self.name,
            op="point_in_direction",
            args=(self._scene.anglesys.to_degree(angle),)))

    def move(self, step):
        """Move this sprite forward by _step_ step.

        The sprite moves by _step_ steps toward the direction it is currently
        pointing to.

        Moving a sprite always takes the same amount of time. Thus, the biggest
        the step is (in absolute value) the faster the sprite moves.

        As a consequence, calling `move(2)' is *not* equivalent to calling
        `move(1)' twice. The sprite will stop at the same position but if it
        takes T seconds to run `move(2)', it will takes 2*T seconds to run
        `move(1)' twice.
        """
        if not isinstance(step, (int, float)):
            raise TypeError("step must be int or float, not {}"
                            .format(type(step).__name__))
        send_request(message.SpriteMove(name=self.name, step=step))

    def _get_state(self):
        return send_request(message.SpriteOp(name=self.name, op="get_state"))

    def position(self):
        return self._scene.coordsys.point_to(self._get_state().position).tuple

    def x_position(self):
        return self.position()[0]

    def y_position(self):
        return self.position()[1]

    def direction(self):
        return self._scene.anglesys.from_degree(self._get_state().direction)

    def bounce_if_on_edge(self):
        st = self._get_state()
        angle_degree = st.direction
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
                dict(op="move_by", args=scene.coordsys.vector_from(Point(dx, dy)).tuple),
            )))

    def turn_counter_clockwise(self, angle):
        self._scene.anglesys.check_angle(angle)
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

    def glide(self, duration, to=None):
        if not isinstance(duration, (int, float)):
            raise TypeError("duration must be int or float, not {}"
                            .format(type(duration).__name__))
        if duration <= 0:
            raise ValueError("duration must be positive")
        if isinstance(to, tuple):
            x, y = to
            if not isinstance(x, (int, float)):
                raise TypeError(f"first destination coordinate must be int or float, not {type(x).__name__}")
            if not isinstance(y, (int, float)):
                raise TypeError(f"second destination coordinate must be int or float, not {type(y).__name__}")
            position = self._scene.coordsys.point_from(Point(x, y)).tuple
        elif isinstance(to, str):
            position = to
        else:
            raise TypeError(f"unexpected type {type(to).__name__} for 'to' argument")
        send_request(message.SpriteMoveTo(
            name=self.name,
            position=position,
            duration=duration))

class Mouse:
    """Mouse state
    """

    # WARNING: Make sure everything is read-only since they are accessed
    #          concurrently.

    __slots__ = ("_engine_mouse", "_coordsys")

    def __init__(self, engine_mouse, coordsys):
        if not isinstance(engine_mouse, EngineMouse):
            raise TypeError("EngineMouse must be scene, not {}"
                            .format(type(EngineMouse).__name__))
        self._engine_mouse = engine_mouse
        self._coordsys = coordsys

    @property
    def position(self):
        return self._coordsys.point_to(Point(*self._engine_mouse.position)).tuple

    @property
    def x(self):
        return self.position()[0]

    @property
    def y(self):
        return self.position()[1]

    @property
    def down(self):
        return any(self._engine_mouse.buttons)

def get_mouse():
    return _MOUSE
