# -*- encoding: utf-8 -*-
"""
"""


import sys
import traceback

from youpy import concurrency
from youpy import message
from youpy.logging import get_user_logger_name
from youpy.logging import getLogger

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
        script = Script(event_handler, self.scene,
                        done_queue=self._done_scripts)
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
    return ".".join((('stage' if event_handler.sprite is None else event_handler.sprite.name),
                     event_handler.callback.__name__))

class Script(concurrency.Task):

    context = concurrency.get_context()

    def __init__(self, event_handler, scene, done_queue=None):
        super().__init__(name=get_script_name(event_handler), daemon=True)
        self.event_handler = event_handler
        self.scene = scene
        self.pipe = concurrency.Pipe()
        self._done_queue = done_queue
        self.exc_info = None

    def run(self):
        self.context.script = self
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
        self.event_handler.callback()

    def send(self, request):
        self.pipe.request_queue.put(request)
        reply = self.pipe.reply_queue.get()
        if isinstance(reply, Exception):
            raise reply
        return reply

    @property
    def sprite(self):
        return self.event_handler.sprite

def get_context_script():
    """Return the script bound to the current thread."""
    return Script.context.script

def send_request(request):
    """Send a request to the engine server."""
    return get_context_script().send(request)

def get_context_sprite_name():
    """Get the name of the sprite bound to the current thread."""
    script = get_context_script()
    sprite = script.sprite
    if sprite is None:
        raise RuntimeError("no sprite associated to this script")
    return sprite.name

def get_scene():
    script = get_context_script()
    return script.scene

def get_script_logger_name():
    script = get_context_script()
    name = get_script_name(script.event_handler)
    return get_user_logger_name(name)

def get_script_logger():
    return getLogger(get_script_logger_name())
