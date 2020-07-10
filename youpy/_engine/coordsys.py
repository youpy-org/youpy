# -*- encoding: utf-8 -*-
"""Coordinate system converter.
"""


import math

from youpy._tools import degree_to_radian
from youpy._tools import radian_to_degree



class coordsys:
    @classmethod
    def get_name(cls):
        return cls.__name__

    DEFAULT = "center"

class center(coordsys):

    def __init__(self, origin):
        self.origin = origin

    def point_to(self, x, y):
        """topleft -> center"""
        return (x - self.origin[0], y - self.origin[1])

    def point_from(self, x, y):
        """center -> topleft"""
        return (self.origin[0] + x, self.origin[1] - y)

class topleft(coordsys):

    def __init__(self, origin):
        pass

    def point_to(self, *args):
        return args

    def point_from(self, *args):
        return args

# compute trigo table
_COSINUS = []
_SINUS = []
for a in range(360):
    _COSINUS.append(math.cos(degree_to_radian(a)))
    _SINUS.append(math.sin(degree_to_radian(a)))
del a

def fast_sin(degree):
    return _SINUS[degree]

def fast_cos(degree):
    return _COSINUS[degree]

class anglesys:
    @classmethod
    def get_name(cls):
        return cls.__name__

    DEFAULT = "scratch_degree"

class degree(anglesys):

    def to(self, radian):
        return radian_to_degree(radian) % 360

    def from_(self, degree):
        return degree_to_radian(degree % 360)

    def to_degree(self, x):
        return x

    def from_degree(self, x):
        return x

class radian(anglesys):

    def to(self, x):
        return x

    def from_(self, x):
        return x

    def to_degree(self, radian):
        return round(radian_to_degree(radian))

    def from_degree(self, degree):
        return degree_to_radian(degree)

class scratch_degree(anglesys):

    def to(self, radian):
        return self.from_degree(radian_to_degree(radian))

    def from_(self, scratch_degree):
        return degree_to_radian(self.to_degree(scratch_degree))

    def to_degree(self, scratch_degree):
        if scratch_degree < 0:
            scratch_degree = 360 + scratch_degree
        return (-scratch_degree + 90) % 360

    def from_degree(self, degree):
        a = (-degree + 90) % 360
        if a > 180:
            a = a - 360
        return round(a)
