# -*- encoding: utf-8 -*-
"""Engine internal "public" API
"""

# This is not in the __init__.py file to prevent importing pygame when
# running the test suite.

from .engine import Engine
from .script import get_scene
from .script import send_request
from .script import get_context_sprite_name
