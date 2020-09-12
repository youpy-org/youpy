# -*- encoding: utf-8 -*-
"""Coordinate system converter.
"""


from youpy.math import degree_to_radian
from youpy.math import radian_to_degree
from youpy.math import Point


class coordsys:
    @classmethod
    def get_name(cls):
        return cls.__name__

    DEFAULT = "center"

class center(coordsys):
    """Converter from 'center' coordinate system to pygame top-left coordinate system."""

    def __init__(self, origin):
        self.origin = origin

    dir_x = 1
    dir_y = -1

    def abscissa_to(self, x):
        return x - self.origin[0]

    def ordinate_to(self, y):
        return self.origin[1] - y

    def point_to(self, p):
        """topleft -> center"""
        return Point(self.abscissa_to(p.x), self.ordinate_to(p.y))

    def abscissa_from(self, x):
        return self.origin[0] + x

    def ordinate_from(self, y):
        return self.origin[1] - y

    def point_from(self, p):
        """center -> topleft"""
        return Point(self.abscissa_from(p.x), self.ordinate_from(p.y))

    def set_rect_position(self, r, p):
        """Set the position of rect _r_ to point _p_.

        r: Rect in center coordinate system
        p: Point in center coordinate system
        """
        r.center = p.discrete.tuple

class topleft(coordsys):

    def __init__(self, origin):
        pass

    dir_x = 1
    dir_y = 1

    def abscissa_to(self, x):
        return x

    def ordinate_to(self, y):
        return y

    def point_to(self, p):
        return p

    def abscissa_from(self, x):
        return x

    def ordinate_from(self, y):
        return y

    def point_from(self, p):
        return p

    def set_rect_position(self, r, p):
        """Set the position of rect _r_ to point _p_.

        r: Rect in top-left coordinate system
        p: Point in top-left coordinate system
        """
        r.topleft = p.discrete.tuple

class anglesys:
    @classmethod
    def get_name(cls):
        return cls.__name__

    DEFAULT = "scratch_degree"

class degree(anglesys):

    def init(self):
        return 0

    def to(self, radian):
        return radian_to_degree(radian) % 360

    def from_(self, degree):
        return degree_to_radian(degree % 360)

    def to_degree(self, x):
        return x

    def from_degree(self, x):
        return x

class radian(anglesys):

    def init(self):
        return 0.0

    def to(self, x):
        return x

    def from_(self, x):
        return x

    def to_degree(self, radian):
        return round(radian_to_degree(radian))

    def from_degree(self, degree):
        return degree_to_radian(degree)

class scratch_degree(anglesys):

    def init(self):
        return 90

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
