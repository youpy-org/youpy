# -*- encoding: utf-8 -*-
"""
"""


import sys
import traceback

from youpy import _concurrency
from . import message


class ScriptSet:

    def __init__(self):
        self._scripts = {}
        self._done_scripts = _concurrency.Queue()

    def bulk_trigger(self, events):
        for event in events:
            self.trigger(event)

    def trigger(self, event):
        script = Script(event, self.scene, done_queue=self._done_scripts)
        self._scripts[script.name] = script
        script.start()

    def rip_done_scripts(self):
        while True:
            try:
                script = self._done_scripts.get(block=False)
            except _concurrency.EmptyQueue:
                break
            else:
                del self._scripts[script.name]
                if script.exc_info is not None:
                    print(f"*** Exception in thread {script.name}")
                    traceback.print_exception(*script.exc_info)

    def join(self, timeout=1.0):
        self._stop_all_scripts()
        unterminated = []
        for s in self._scripts.values():
            s.join(timeout=timeout)
            if s.is_alive():
                unterminated.append(s)
        # TODO(Nicolas Despres): Move the printing to engine?
        if unterminated:
            print(f"There were {len(unterminated)} unterminated scripts:")
            for s in unterminated:
                print(f"  {s.name}")
            return False
        return True

    def _stop_all_scripts(self):
        for script in self._scripts.values():
            script.pipe.reply_queue.put(message.StopScript())

    def __iter__(self):
        return iter(self._scripts.values())

    def __len__(self):
        return len(self._scripts)

class StopScript(Exception):
    pass

def get_script_name(event):
    return ".".join((('stage' if event.sprite is None else event.sprite.name),
                     event.callback.__name__))

class Script(_concurrency.Task):

    context = _concurrency.get_context()

    def __init__(self, event, scene, done_queue=None):
        super().__init__(name=get_script_name(event), daemon=True)
        self.event = event
        self.scene = scene
        self.pipe = _concurrency.Pipe()
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
        self.event.callback()

    def send(self, request):
        self.pipe.request_queue.put(request)
        reply = self.pipe.reply_queue.get()
        if isinstance(reply, Exception):
            raise reply
        return reply

    @property
    def sprite(self):
        return self.event.sprite

def get_context_script():
    return Script.context.script

def send_request(request):
    get_context_script().send(request)

def get_context_sprite_name():
    script = get_context_script()
    sprite = script.sprite
    if sprite is None:
        raise RuntimeError("no sprite associated to this script")
    return sprite.name

def get_scene():
    script = get_context_script()
    return script.scene
