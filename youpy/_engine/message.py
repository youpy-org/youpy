# -*- encoding: utf-8 -*-
"""
"""


from typing import Any
from typing import Tuple
from typing import Mapping
from dataclasses import dataclass
from dataclasses import field


class StopScript:
    pass

@dataclass
class SharedVariableNew:
    name: str
    value: Any

@dataclass
class SharedVariableDel:
    name: str

@dataclass
class SharedVariableOp:
    name: str
    op: str
    args: Tuple[Any] = ()
    kwargs: Mapping[str, Any] = field(default_factory=dict)

@dataclass
class BackdropSwitchTo:
    name: str

@dataclass
class SpriteOp:
    name: str
    op: str
    args: Tuple[Any] = ()
    kwargs: Mapping[str, Any] = field(default_factory=dict)

@dataclass
class SpriteGetCollision:
    name: str

@dataclass
class SpriteBatchOp:
    name: str
    ops: Tuple[Mapping]
