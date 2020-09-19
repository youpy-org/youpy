from youpy.code.english.everything import *
from time import time

# Useful to compare sprite moving speed between Youpy and Scratch.
# We aim to have roughly the same speed.
# See EngineSprite.MOVE_DURATION constant.

def when_program_start():
    X0 = -230
    go_to(X0, 0)

    console.print("duration must be invariant by fps")

    N = 200
    S = 2
    t0 = time()
    for _ in range(N):
        move(S)
    t1 = time()
    duration = t1 - t0
    console.print(f"{duration=}")

    assert position() == (X0 + N * S, 0)

    stop_program(reason="end of experiment")
