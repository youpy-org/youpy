# -*- encoding: utf-8 -*-
"""
"""


import unittest


from youpy.math import Point


class TestPoint(unittest.TestCase):

    def test_negq(self):
        self.assertEqual(-Point(2, 4), Point(-2, -4))

    def test_pos(self):
        self.assertEqual(+Point(2, 4), Point(+2, +4))

    def test_abs(self):
        self.assertEqual(abs(Point(2, -4)), Point(2, 4))

    def test_eq(self):
        self.assertEqual(Point(2, 4), Point(2, 4))

    def test_neq(self):
        self.assertNotEqual(Point(4, 2), Point(2, 4))

    def test_imul(self):
        p = Point(1, 2)
        p *= 3
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 6)

    def test_mul(self):
        self.assertEqual(Point(1, 2) * 3, Point(3, 6))

    def test_rmul(self):
        self.assertEqual(3 * Point(1, 2), Point(3, 6))
