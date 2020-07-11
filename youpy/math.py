# -*- encoding: utf-8 -*-
"""
"""


from math import pi
from math import sin
from math import cos
from math import tan
from math import atan2


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

def fast_sin(degree):
    return _SINUS[degree]

def fast_cos(degree):
    return _COSINUS[degree]

def fast_tan(degree):
    return _TANS[degree]
