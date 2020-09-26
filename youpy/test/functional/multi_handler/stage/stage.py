from youpy.code.english.everything import *

def when_program_start__1():
    for i in range(5):
        console.print(f"thread 1 count {i}")
        wait(1)

def when_program_start__2():
    for i in range(10):
        console.print(f"thread 2 count {i}")
        wait(0.5)
