# -*- encoding: utf-8 -*-
"""
"""


from abc import ABC
from abc import abstractmethod

from youpy import logging
LOGGER = logging.getLogger(__name__)


class PhysicalSystem(ABC):

    def __init__(self):
        self.__result = None
        self.__finished = False

    def step(self):
        """Run one physical step of the system."""
        try:
            self._on_step()
        except Exception as e:
            self._set_result(e)

    @abstractmethod
    def _on_step(self):
        pass

    def start(self):
        try:
            self._on_start()
        except Exception as e:
            self._set_result(e)

    def _on_start(self):
        pass

    @property
    def is_finished(self):
        return self.__finished

    @property
    def result(self):
        return self.__result

    def _set_result(self, result):
        self.__result = result
        self.__finished = True

    def _set_result_if(self, condition, result=None):
        if condition:
            self._set_result(result)

class PhysicalEngine:

    def __init__(self, delta_time=10):
        """
        Parameters:
        - delta_time: duration in milliseconds of one physic simulation step.
        """
        if not isinstance(delta_time, int):
            raise TypeError("delta_time must be int, not {}"
                            .format(type(delta_time).__name__))
        self._delta_time = delta_time
        self._time = 0 # Total simulated time elapsed since the simulation boot
        self._scheduled_systems = []
        self._running_systems = []

    @property
    def delta_time(self):
        return self._delta_time

    @property
    def time(self):
        return self._time

    def step(self):
        """Simulate one step of physical time."""
        ### Start new systems
        for new_system in self._scheduled_systems:
            self._start(new_system)
            self._running_systems.append(new_system)
        self._scheduled_systems.clear()
        ### Run systems
        still_running_systems = []
        for running_system in self._running_systems:
            if not running_system.is_finished:
                running_system.step()
                still_running_systems.append(running_system)
        self._running_systems = still_running_systems
        # Must be the last statement
        self._time += self._delta_time

    def schedule(self, system):
        self._scheduled_systems.append(system)

    def _start(self, system):
        system.engine = self
        system._on_start()
