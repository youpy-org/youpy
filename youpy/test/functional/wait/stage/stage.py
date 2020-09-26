from youpy.code.english.control import wait
from youpy.code.english.control import console
from time import time

def when_program_start():
    console.print("program is starting")
    t0 = time()
    wait(10)
    t1 = time()
    console.print(f"waited {t1 - t0:.4f}s")
    console.print("program finished")
