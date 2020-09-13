from youpy.code.english.everything import *
from time import time

def when_space_key_pressed():
    go_to(-230, 0)

    console.print("All durations should be roughly equal")

    t0 = time()
    for _ in range(50):
        move(2)
    t1 = time()
    console.print(t1 - t0)

    for _ in range(50):
        move(1)
        move(1)
    t2 = time()
    console.print(t2 - t1)

    for _ in range(50):
        move(2)
        bounce_if_on_edge()
    t3 = time()
    console.print(t3 - t2)

    console.print(f"total time: {t3 - t0}")
    stop_program(reason="end of experiment")
