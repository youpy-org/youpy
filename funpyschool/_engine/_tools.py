# -*- encoding: utf-8 -*-
"""
"""


import time


class FrequencyMeter:

    def __init__(self):
        self._count = 0
        self._frequency = 0.0
        self._last_updated_at = 0.0
        self._updated = False

    def update(self):
        t = time.time()
        duration = (t - self._last_updated_at)
        if duration > 1.0: # sec
            self._frequency = self._count / duration
            self._count = 0
            self._last_updated_at = t
            self._updated = True
        else:
            self._count += 1
            self._updated = False
        return self._updated

    @property
    def frequency(self):
        return self._frequency

    @property
    def updated(self):
        return self._updated

    def __str__(self):
        return f"{self._frequency:.2f}"

    def __repr__(self):
        return f"{self.__class__.__name__}(count={self.count}, "\
            f"frequency={self._frequency}, "\
            f"last_updated_at={self._last_updated_at})"
