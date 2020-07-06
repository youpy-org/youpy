# -*- encoding: utf-8 -*-
"""Coordinate system converter.
"""


DEFAULT = "center"

class center:

    def __init__(self, origin):
        self.origin = origin

    def point_to(self, x, y):
        """topleft -> center"""
        return (x - self.origin[0], y - self.origin[1])

    def point_from(self, x, y):
        """center -> topleft"""
        return (self.origin[0] + x, self.origin[1] - y)

    # def rect_to(self, rect):
    #     """topleft -> center"""
    #     return type(rect)(self.point_to(rect.topleft), rect.size)

    def rect_go_to(self, rect, x, y):
        """Move _rect_ to point (x, y).

        Arguments:
          rect: a rectangle topleft coordinate-system
          x, y: a point in center coordinate-system
        """
        rect.center = self.point_from(x, y)

class topleft:

    def __init__(self, scene):
        pass

    def point_to(self, *args):
        return args

    def point_from(self, *args):
        return args
