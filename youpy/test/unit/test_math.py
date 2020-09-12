# -*- encoding: utf-8 -*-
"""
"""


import unittest


from youpy.math import Point


class TestPoint(unittest.TestCase):

    def test_imul(self):
        p = Point(1, 2)
        p *= 3
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 6)
