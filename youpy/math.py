# -*- encoding: utf-8 -*-
"""
"""


from math import pi
from math import sin
from math import cos
from math import tan
from math import atan2
from math import sqrt
from math import isclose
from math import ceil
from math import floor
from collections import OrderedDict


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

discretize = int

# TODO(Nicolas Despres): unit test this class
class Point:

    __slots__ = ("_x", "_y")

    @classmethod
    def null(cls):
        return cls(0, 0)

    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, x):
        self._x = x

    @y.setter
    def y(self, y):
        self._y = y

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
        return self

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
        return self

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
        return self

    def __mul__(self, scalar):
        p = self.copy()
        p *= scalar
        return p

    def __rmul__(self, scalar):
        p = self.copy()
        p *= scalar
        return p

    def __itruediv__(self, obj):
        if isinstance(obj, (int, float)):
            self._x /= obj
            self._y /= obj
        else:
            raise NotImplementedError(f"cannot multiply a {type(self).__name__} by a '{type(obj).__name__}'")
        return self

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
        return self

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

    @property
    def tuple(self):
        return (self._x, self._y)

    def set(self, point):
        if not isinstance(point, Point):
            raise TypeError("point must be Point, not {}"
                            .format(type(point).__name__))
        self._x = point.x
        self._y = point.y

    @property
    def discrete(self):
        return Point(discretize(self.x), discretize(self.y))

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

    @property
    def tuple(self):
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

class _BaseSystem:
    """Mix-in for the meta class"""

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def get_system(cls, name):
        return cls._systems[name]

class _MetaSystem(type):

    _systems = OrderedDict()

    @classmethod
    def __prepare__(meetacls, name, bases, **kwargs):
        return OrderedDict()

    def __new__(metacls, name, bases, namespace, **kwargs):
        cls = super().__new__(metacls, name, bases, namespace, **kwargs)
        if bases == (_BaseSystem,): # base class
            cls._systems = OrderedDict()
        else:
            cls._systems[name] = cls
        return cls

class CoordSys(_BaseSystem, metaclass=_MetaSystem):

    DEFAULT = "center"

class center(CoordSys):
    """Converter from 'center' coordinate system to pygame top-left coordinate system."""

    def __init__(self, origin):
        self.origin = origin

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

    def vector_from(self, v):
        """center -> topleft"""
        return Point(v.x, -v.y)

    def vector_to(self, v):
        """topleft -> center"""
        return Point(v.x, -v.y)

class topleft(CoordSys):

    def __init__(self, origin):
        pass

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

    def vector_from(self, v):
        return v

    def vector_to(self, v):
        return v

class AngleSys(_BaseSystem, metaclass=_MetaSystem):

    DEFAULT = "scratch_degree"

class degree(AngleSys):

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

    def check_angle(self, angle):
        check_degree_angle(angle)

    def inc_angle(self, angle, inc):
        angle += inc
        angle %= 360
        return angle

class radian(AngleSys):

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

    def check_angle(self, angle):
        if not isinstance(angle, (int, float)):
            raise TypeError("angle must be int or float, not {}"
                            .format(type(angle).__name__))

    def inc_angle(self, angle, inc):
        angle += inc
        return angle

class scratch_degree(AngleSys):

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

    def check_angle(self, angle):
        check_degree_angle(angle)

    def inc_angle(self, angle, inc):
        angle += inc
        if angle > 180:
            angle -= 360
        elif angle < -180:
            angle += 360
        return angle

def check_degree_angle(angle):
    if not isinstance(angle, int):
        raise TypeError("angle must be int, not {}"
                        .format(type(angle).__name__))
    if not 0 <= angle < 360:
        raise ValueError(
            "angle must be between 0 and 360 degrees excluded, "\
            f"but is equal to {angle}")
