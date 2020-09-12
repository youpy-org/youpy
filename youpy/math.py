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
