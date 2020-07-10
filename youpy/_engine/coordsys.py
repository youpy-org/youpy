# -*- encoding: utf-8 -*-
"""Coordinate system converter.
"""


DEFAULT = "center"

class coordsys:
    @classmethod
    def get_name(cls):
        return cls.__name__

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

    def __init__(self):
        pass

    def point_to(self, *args):
        return args

    def point_from(self, *args):
        return args
