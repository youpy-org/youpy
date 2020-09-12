# -*- encoding: utf-8 -*-
"""
"""


from math import pi
from math import sin
from math import cos
from math import tan
from math import atan2
from math import sqrt


def degree_to_radian(degree):
    return degree * pi / 180

def radian_to_degree(radian):
    return radian * 180 / pi

# compute trigo table
_COSINUS = []
_SINUS = []
_TANS = []
for a in range(360):
    r = degree_to_radian(a)
    _COSINUS.append(cos(r))
    _SINUS.append(sin(r))
    _TANS.append(tan(r))
del a, r
_COSINUS[90] = 0.0
_COSINUS[270] = -0.0
_SINUS[0] = 0.0
_SINUS[180] = -0.0
_TANS[0] = 0.0
_TANS[180] = -0.0
_TANS[45] = 1.0
_TANS[3*45] = -1.0
_TANS[5*45] = 1.0
_TANS[7*45] = -1.0

def fast_sin(degree):
    return _SINUS[degree]

def fast_cos(degree):
    return _COSINUS[degree]

def fast_tan(degree):
    return _TANS[degree]

def norm(x, y):
    return sqrt(x ** 2 + y ** 2)

# TODO(Nicolas Despres): unit test this class
class Point:

    __slots__ = ("_x", "_y")

    @classmethod
    def null(cls):
        return cls(0.0, 0.0)

    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def copy(self):
        return type(self)(self._x, self._y)

    def __iadd__(self, obj):
        if isinstance(obj, Point):
            self._x += obj.x
            self._y += obj.y
        elif isinstance(obj, (int, float)):
            self._x += obj
            self._y += obj
        else:
            raise NotImplementedError(f"cannot add a '{type(obj).__name__}' to a Point")

    def __add__(self, obj):
        p = self.copy()
        p += obj
        return p

    def __isub__(self, obj):
        if isinstance(obj, Point):
            self._x -= obj.x
            self._y -= obj.y
        elif isinstance(obj, (int, float)):
            self._x -= obj
            self._y -= obj
        else:
            raise NotImplementedError(f"cannot add a '{type(obj).__name__}' to a {type(self).__name__}")

    def __sub__(self, obj):
        p = self.copy()
        p -= obj
        return p

    def __imul__(self, obj):
        if isinstance(obj, (int, float)):
            self._x *= obj
            self._y *= obj
        else:
            raise NotImplementedError(f"cannot multiply a {type(self).__name__} by a '{type(obj).__name__}'")

    def __mul__(self, scalar):
        p = self.copy()
        p *= scalar
        return p

    def __itruediv__(self, obj):
        if isinstance(obj, (int, float)):
            self._x /= obj
            self._y /= obj
        else:
            raise NotImplementedError(f"cannot multiply a {type(self).__name__} by a '{type(obj).__name__}'")

    def __truediv__(self, scalar):
        p = self.copy()
        p /= scalar
        return p

    def __ipow__(self, obj):
        if isinstance(obj, (int, float)):
            self._x **= obj
            self._y **= obj
        else:
            raise NotImplementedError(f"'{type(obj).__name__}' is not a valid power of a {type(self).__name__}")

    def __pow__(self, obj):
        p = Point.copy()
        p **= obj
        return p

    def __neg__(self):
        return Point(-self._x, -self._y)

    def __pos__(self):
        return self.copy()

    def __abs__(self):
        return Point(abs(self._x), abs(self._y))

    def __repr__(self):
        return f"{type(self).__name__}({self._x}, {self._y})"

    def norm(self):
        return norm(self._x, self._y)

    def normalize(self):
        self /= self.norm()

    def __eq__(self, obj):
        if isinstance(obj, Point):
            return self._x == obj.x and self._y == obj.y
        else:
            raise NotImplementedError(f"cannot test equality between a {type(self).__name__} and a {type(obj).__name__}")

    def __ne__(self, obj):
        if isinstance(obj, Point):
            return self._x != obj.x or self._y != obj.y
        else:
            raise NotImplementedError(f"cannot test inequality between a {type(self).__name__} and a {type(obj).__name__}")

    def nullify(self):
        self._x = 0
        self._y = 0

    def to_tuple(self):
        return (self._x, self._y)

    def set(self, point):
        if not isinstance(point, Point):
            raise TypeError("point must be Point, not {}"
                            .format(type(point).__name__))
        self._x = point.x
        self._y = point.y



class Size:

    __slots__ = ("_w", "_h")

    @classmethod
    def null(cls):
        return cls(0, 0)

    def __init__(self, width, height):
        self._w = width
        self._h = height

    @property
    def width(self):
        return self._w

    @property
    def height(self):
        return self._h

    def to_tuple(self):
        return (self._w, self._h)

    def set(self, obj):
        if isinstance(obj, Size):
            self._w = obj._w
            self._h = obj._h
        elif isinstance(obj, tuple):
            self._w, self._h = obj
        else:
            raise TypeError("obj must be Size or tuple, not {}"
                            .format(type(new_size).__name__))
