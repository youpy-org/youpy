# -*- encoding: utf-8 -*-
"""
"""


from youpy import _concurrency
from . import message


class ScriptSet:

    def __init__(self):
        self._scripts = {}

    def bulk_trigger(self, events):
        for event in events:
            self.trigger(event)

    def trigger(self, event):
        script = Script(event, done_callback=self._on_script_done)
        self._scripts[script.name] = script
        script.start()

    def _on_script_done(self, script):
        del self._scripts[script.name]

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
    return "_".join((('stage' if event.sprite is None else event.sprite.name),
                     event.callback.__name__))

class Script(_concurrency.Task):

    context = _concurrency.get_context()

    def __init__(self, event, done_callback=None):
        super().__init__(name=get_script_name(event), daemon=True)
        self.event = event
        self.pipe = _concurrency.Pipe()
        self.done_callback = done_callback

    def run(self):
        self.context.script = self
        try:
            self._run()
        except StopScript:
            pass
        finally:
            self.done_callback(self)

    def _run(self):
        self.event.callback()

    def send(self, request):
        self.pipe.request_queue.put(request)
        reply = self.pipe.reply_queue.get()
        if isinstance(reply, Exception):
            raise reply
        return reply

def send_request(request):
    Script.context.script.send(request)
