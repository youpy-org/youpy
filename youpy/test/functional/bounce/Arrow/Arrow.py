from youpy.code.english.everything import *
from time import time
import math

def when_space_key_pressed():
    go_to(-230, 0)

    console.print("duration must be invariant by fps")

    ### 1
    t0 = time()
    for _ in range(50):
        move(2)
    t1 = time()
    d1 = t1 - t0
    console.print(f"{d1=}")

    ### 2
    for _ in range(50):
        move(1)
        move(1)
    t2 = time()
    d2 = t2 - t1
    console.print(f"{d2=}")
    # assert math.isclose(2*d1, d2)

    ### 3
    # Should be as fast as the first loop
    for _ in range(50):
        move(2)
        for _ in range(50):
            x_position()
    t3 = time()
    d3 = t3 - t2
    console.print(f"{d3=}")
    # assert math.isclose(d3, d1)

    console.print(f"total time: {t3 - t0}")
    stop_program(reason="end of experiment")
