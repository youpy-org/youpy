# -*- encoding: utf-8 -*-
"""
"""


from math import pi
from math import sin
from math import cos
from math import atan2


def degree_to_radian(degree):
    return degree * pi / 180

def radian_to_degree(radian):
    return radian * 180 / pi

# compute trigo table
_COSINUS = []
_SINUS = []
for a in range(360):
    _COSINUS.append(cos(degree_to_radian(a)))
    _SINUS.append(sin(degree_to_radian(a)))
del a

def fast_sin(degree):
    return _SINUS[degree]

def fast_cos(degree):
    return _COSINUS[degree]
