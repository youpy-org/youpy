from youpy.code.english.everything import *
from time import time
import math

def when_space_key_pressed():
    go_to(-230, 0)

    console.print("duration must be invariant by fps")

    t0 = time()
    for _ in range(50):
        move(2)
    t1 = time()
    d1 = t1 - t0
    console.print(f"{d1=}")

    for _ in range(50):
        move(1)
        move(1)
    t2 = time()
    d2 = t2 - t1
    console.print(f"{d2=}")
    # assert math.isclose(2*d1, d2)

    for _ in range(50):
        move(2)
        bounce_if_on_edge()
    t3 = time()
    d3 = t3 - t2
    console.print(f"{d3=}")

    console.print(f"total time: {t3 - t0}")
    stop_program(reason="end of experiment")
