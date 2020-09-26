from youpy.code.english.everything import *

def when_program_start():
    while True:
        if Mouse.down:
            console.print(f"mouse position {Mouse.position}")
            console.print(f"mouse pressed")
