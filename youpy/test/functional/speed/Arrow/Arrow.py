from youpy.code.english.everything import *
from time import time

# Useful to compare sprite moving speed between Youpy and Scratch.
# We aim to have roughly at the same speed.
# See EngineSprite.MOVE_DURATION constant.
#
# The duration of this test is supposed to be invariant by fps. But the
# bigger the move step (S) the smaller the difference is between 15fps and
# 90fps. This is due to the time required to process move instruction.
# For the same distance, there will be less move() call if the step is large.
# When the step is small, we start to be bound by the time required to process
# the move instructions. So, even with the same fps, we get different duration
# between (N=400; S=1) and (N=5; S=80).

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
