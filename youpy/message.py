# -*- encoding: utf-8 -*-
"""
"""


from typing import Any
from typing import Tuple
from typing import Mapping
from typing import Union
from dataclasses import dataclass
from dataclasses import field

from youpy import math


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

@dataclass
class SpriteMove:
    name: str
    step: Union[int, float]

@dataclass
class SpriteMoveBy:
    name: str
    step_by: math.Point

@dataclass
class SpriteMoveTo:
    name: str
    position: Tuple[Union[int, float], Union[int, float]]

@dataclass
class Wait:
    delay: float

@dataclass
class StopProgram:
    reason: str
