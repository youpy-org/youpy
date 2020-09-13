from youpy.code.english.everything import *
from time import time

# Useful to compare sprite moving speed between Youpy and Scratch.
# We aim to have roughly the same speed.
# See EngineSprite.MOVE_DURATION constant.

def when_space_key_pressed():
    go_to(-230, 0)

    console.print("duration must be invariant by fps")

    t0 = time()
    for _ in range(200):
        move(2)
    t1 = time()
    duration = t1 - t0
    console.print(f"{duration=}")

    stop_program(reason="end of experiment")
