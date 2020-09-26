from youpy.code.english.everything import *
from time import time
import math

def when_program_start():
    go_to(point=Stage.center)
    D = 2.5
    while True:
        t0 = time()
        p = Stage.random_position
        glide(D, to=p)
        t1 = time()
        assert math.isclose(round(t1 - t0, 1), D)
        assert position() == p
