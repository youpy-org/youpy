# -*- encoding: utf-8 -*-
"""Youpy's internal "public" API

This API is the interface between Youpy's core engine and the front-end API
code available in users projects.
"""

# This is not in the __init__.py file to prevent importing pygame when
# running the test suite.

# It also centralize, part of the framework that are directly used by the
# front-end module in the `code` sub-package.

from youpy.engine import Engine
from youpy.script import get_scene
from youpy.script import send_request
from youpy.script import StopScript
from youpy.script import get_script_logger
from youpy.script import Sprite
from youpy.script import get_context_frontend_sprite
from youpy.runner import run
from youpy import message
from youpy import math
from youpy.data import SCENE_EDGE
