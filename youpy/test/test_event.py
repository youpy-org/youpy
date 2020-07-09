# -*- encoding: utf-8 -*-
"""
"""


import unittest
from collections import defaultdict

from youpy._engine.event import EventHandlers
from youpy._engine.event import EventHandler
from youpy._engine.event import ProgramStart
from youpy._engine.event import BackdropSwitches


class TestEventProgramStart(unittest.TestCase):

    def test_hash(self):
        self.assertEqual(hash(ProgramStart()), hash(ProgramStart()))

    def test_in_set(self):
        s = set()
        s.add(ProgramStart())
        self.assertIn(ProgramStart(), s)

class TestEventBackdropSwitches(unittest.TestCase):

    def test_hash(self):
        self.assertEqual(hash(BackdropSwitches(backdrop="foo")),
                         hash(BackdropSwitches(backdrop="foo")))
        self.assertNotEqual(hash(BackdropSwitches(backdrop="foo")),
                            hash(BackdropSwitches(backdrop="bar")))

    def test_in_set(self):
        s = set()
        s.add(BackdropSwitches(backdrop="foo"))
        self.assertIn(BackdropSwitches(backdrop="foo"), s)
        self.assertNotIn(BackdropSwitches(backdrop="bar"), s)

    def test_value_affect_equality(self):
        s = set()
        s.add(BackdropSwitches(backdrop="foo"))
        s.add(BackdropSwitches(backdrop="bar"))
        self.assertEqual(2, len(s))

class TestEventHandlers(unittest.TestCase):

    def test_get(self):
        eh = EventHandlers()
        e = ProgramStart()
        h = EventHandler(callback=lambda: 42)
        eh.register(e, h)
        handlers = eh.get(ProgramStart())
        self.assertEqual(1, len(handlers))
        self.assertIs(handlers[0], h)
