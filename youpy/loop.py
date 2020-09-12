# -*- encoding: utf-8 -*-
"""
"""


from abc import ABC
from abc import abstractmethod
import time

import pygame


class EngineLoop(ABC):

    def __init__(self, render, simulate):
        self.render = render
        self.simulate = simulate
        self.started_at = time.time()

    @abstractmethod
    def step(self):
        pass

    @property
    def elapsed_time(self):
        return time.time() - self.started_at

class FixedDeltaTimeEngineLoop(EngineLoop):

    def __init__(self, render, simulate, dt):
        super().__init__(render, simulate)
        self.dt = dt
        self.clock = pygame.time.Clock()

    def step(self):
        self.simulate()
        self.render()
        self.clock.tick_busy_loop(self.dt)
