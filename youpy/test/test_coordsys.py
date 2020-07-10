# -*- encoding: utf-8 -*-
"""
"""


import unittest
import math

from youpy._engine import coordsys


class TestScratchDegree(unittest.TestCase):

    def setUp(self):
        self.cs = coordsys.scratch_degree()

    # radian -> degree
    REF_TABLE = (
        ("  -2*math.pi",   90),
        ("-7*math.pi/4",   45),
        ("-3*math.pi/2",    0),
        ("-5*math.pi/4",  -45),
        ("    -math.pi",  -90),
        ("-3*math.pi/4", -135),
        ("  -math.pi/2",  180),
        ("  -math.pi/4",  135),
        ("           0",   90),
        ("   math.pi/4",   45),
        ("   math.pi/2",    0),
        (" 3*math.pi/4",  -45),
        ("     math.pi",  -90),
        (" 5*math.pi/4", -135),
        (" 3*math.pi/2",  180),
        (" 7*math.pi/4",  135),
        ("   2*math.pi",   90),
    )

    def test_to(self):
        for radian, degree in self.REF_TABLE:
            with self.subTest(radian=radian, degree=degree):
                self.assertEqual(self.cs.to(eval(radian)), degree)

    def test_from(self):
        for radian, degree in self.REF_TABLE:
            with self.subTest(radian=radian, degree=degree):
                self.assertEqual(self.cs.from_(degree),
                                 eval(radian) % (2 * math.pi))
