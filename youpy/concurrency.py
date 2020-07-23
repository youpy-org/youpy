# -*- encoding: utf-8 -*-
"""Group all concurrency objects and routines we use.

Intended to easy a potential future change in the concurrency model (i.e.
threads VS processes)
"""


# TODO(Nicolas Despres): Completely wrap the Queue and Task classes for proper
#  abstraction.

import threading as _concurrency
import queue as _queue

Task = _concurrency.Thread
Queue = _queue.Queue
EmptyQueue = _queue.Empty

def get_context():
    return _concurrency.local()

class Pipe:

    MAXSIZE = 10

    def __init__(self):
        self.request_queue = Queue(maxsize=self.MAXSIZE)
        self.reply_queue = Queue(maxsize=self.MAXSIZE)
