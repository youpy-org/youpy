# -*- encoding: utf-8 -*-
"""
"""


from youpy import math
from youpy import logging
LOGGER = logging.getLogger(__name__)


class SpriteMoveSystem:

    __slots__ = ("_sprite", "_velocity", "_destination", "_step_count")

    def __init__(self, sprite, velocity, destination, step_count):
        self._sprite = sprite
        self._velocity = velocity
        self._destination = destination
        self._step_count = step_count

    def _step(self):
        self._sprite.move_by_velocity(self._velocity)
        self._step_count -= 1
        if self._step_count == 0:
            # Move the sprite to the final position in all cases so that
            # if MOVE_DURATION is not a multiple of delta_time, we still end-up
            # at the right position.
            self._sprite.go_to_position(self._destination)

    @property
    def is_finished(self):
        return self._step_count <= 0

# The time a sprite takes to move from one point from another.
SPRITE_MOVE_DURATION = 0.02 # seconds

class PhysicalEngine:

    def __init__(self, delta_time=0.01):
        """
        Parameters:
        - delta_time: duration in seconds of one physic simulation step.
        """
        self._delta_time = delta_time
        self._time = 0 # Total simulated time elapsed since the simulation boot
        self._running_systems = []

    @property
    def delta_time(self):
        return self._delta_time

    @property
    def time(self):
        return self._time

    def step(self):
        """Simulate one step of physical time."""
        ### Run systems
        still_running_systems = []
        for running_system in self._running_systems:
            if not running_system.is_finished:
                running_system._step()
                still_running_systems.append(running_system)
        self._running_systems = still_running_systems
        # Must be the last statement
        self._time += self._delta_time

    def move_sprite(self, sprite, step, duration=SPRITE_MOVE_DURATION):
        if step == 0:
            system = SpriteMoveSystem(sprite, Point.null(), sprite.position, 0)
        else:
            step_count = self._get_step_count(duration)
            velocity = sprite.get_velocity_from_direction()
            destination = sprite.position + step * velocity
            inc_step = step / step_count
            velocity *= inc_step
            system = SpriteMoveSystem(sprite, velocity, destination, step_count)
        self._running_systems.append(system)
        return system

    def move_sprite_by(self, sprite, velocity, duration=SPRITE_MOVE_DURATION):
        if velocity.is_null:
            system = SpriteMoveSystem(sprite, velocity, sprite.position, 0)
        else:
            destination = sprite.position + velocity
            step_count = self._get_step_count(duration)
            velocity /= step_count
            system = SpriteMoveSystem(sprite, velocity / step_count, destination, step_count)
        self._running_systems.append(system)
        return system

    def move_sprite_to(self, sprite, position,
                       duration=SPRITE_MOVE_DURATION):
        x, y = position
        if x is None:
            x = sprite.position.x
        if y is None:
            y = sprite.position.y
        destination = math.Point(x, y)
        step_count = self._get_step_count(duration)
        velocity = (destination - sprite.position) / step_count
        system = SpriteMoveSystem(sprite, velocity, destination, step_count)
        self._running_systems.append(system)
        return system

    def _get_step_count(self, duration):
        step_count = math.floor(duration / self.delta_time)
        assert step_count > 0, "duration must be higher than simulation delta-time"
        return step_count
