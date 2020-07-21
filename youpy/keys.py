# -*- encoding: utf-8 -*-
"""
"""


from dataclasses import dataclass

import pygame


@dataclass
class Key:
    name: str
    code: int

class Keys:
    space       = Key(name="space",       code=(pygame.K_SPACE,))
    up_arrow    = Key(name="up_arrow",    code=(pygame.K_UP,))
    down_arrow  = Key(name="down_arrow",  code=(pygame.K_DOWN,))
    left_arrow  = Key(name="left_arrow",  code=(pygame.K_LEFT,))
    right_arrow = Key(name="right_arrow", code=(pygame.K_RIGHT,))
    a           = Key(name="a",           code=(pygame.K_a,))
    b           = Key(name="b",           code=(pygame.K_b,))
    c           = Key(name="c",           code=(pygame.K_c,))
    d           = Key(name="d",           code=(pygame.K_d,))
    e           = Key(name="e",           code=(pygame.K_e,))
    f           = Key(name="f",           code=(pygame.K_f,))
    g           = Key(name="g",           code=(pygame.K_g,))
    h           = Key(name="h",           code=(pygame.K_h,))
    i           = Key(name="i",           code=(pygame.K_i,))
    j           = Key(name="j",           code=(pygame.K_j,))
    k           = Key(name="k",           code=(pygame.K_k,))
    l           = Key(name="l",           code=(pygame.K_l,))
    m           = Key(name="m",           code=(pygame.K_m,))
    n           = Key(name="n",           code=(pygame.K_n,))
    o           = Key(name="o",           code=(pygame.K_o,))
    p           = Key(name="p",           code=(pygame.K_p,))
    q           = Key(name="q",           code=(pygame.K_q,))
    r           = Key(name="r",           code=(pygame.K_r,))
    s           = Key(name="s",           code=(pygame.K_s,))
    t           = Key(name="t",           code=(pygame.K_t,))
    u           = Key(name="u",           code=(pygame.K_u,))
    v           = Key(name="v",           code=(pygame.K_v,))
    w           = Key(name="w",           code=(pygame.K_w,))
    x           = Key(name="x",           code=(pygame.K_x,))
    y           = Key(name="y",           code=(pygame.K_y,))
    z           = Key(name="z",           code=(pygame.K_z,))
    one         = Key(name="1",           code=(pygame.K_1, pygame.K_KP1))
    two         = Key(name="2",           code=(pygame.K_2, pygame.K_KP2))
    three       = Key(name="3",           code=(pygame.K_3, pygame.K_KP3))
    four        = Key(name="4",           code=(pygame.K_4, pygame.K_KP4))
    five        = Key(name="5",           code=(pygame.K_5, pygame.K_KP5))
    six         = Key(name="6",           code=(pygame.K_6, pygame.K_KP6))
    seven       = Key(name="7",           code=(pygame.K_7, pygame.K_KP7))
    eight       = Key(name="8",           code=(pygame.K_8, pygame.K_KP8))
    nine        = Key(name="9",           code=(pygame.K_9, pygame.K_KP9))
    zero        = Key(name="0",           code=(pygame.K_0, pygame.K_KP0))

def iter_keys():
    for attr in dir(Keys):
        if attr.startswith("_"):
            continue
        key = getattr(Keys, attr)
        yield key

def check_key(key_name):
    if not isinstance(key_name, str):
        raise TypeError("key_name must be str, not {}"
                        .format(type(key_name).__name__))
    if not hasattr(Keys, key_name):
        raise ValueError(f"invalid key: '{key_name}'")

__all__ = (
    "Keys",
    "iter_keys",
)
