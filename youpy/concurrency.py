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

# Copied from https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s04.html
class ReadWriteLock:
    """Lock allowing shared read access but exclusive write access.
    """

    def __init__(self):
        self._read_ready = _concurrency.Condition(_concurrency.Lock())
        self._readers_count = 0

    def acquire_read(self):
        """Acquire a read lock.

        Blocks only if a thread has acquired the write lock.
        """
        self._read_ready.acquire()
        try:
            self._readers_count += 1
        finally:
            self._read_ready.release()

    def release_read(self):
        """Release a read lock."""
        self._read_ready.acquire()
        try:
            self._readers_count -= 1
            if self._readers_count <= 0:
                self._read_ready.notifyAll()
        finally:
            self._read_ready.release()

    def acquire_write(self):
        """Acquire a write lock.

        Blocks until there are no acquired read or write locks.
        """
        self._read_ready.acquire()
        while self._readers_count > 0:
            self._read_ready.wait()

    def release_write(self):
        """Release a write lock."""
        self._read_ready.release()
