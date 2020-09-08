from youpy.code.english.control import wait
from youpy.code.english.control import console

def when_program_start():
    console.print("program is starting")
    wait(60)
    console.print("program finished")
