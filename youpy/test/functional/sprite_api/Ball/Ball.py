from youpy.code.english.control import console
from youpy.code.english.control import wait
from youpy.code.english.motion import change_y_by

def when_program_start(sprite):
    console.print(f"Hello from Sprite '{sprite.name}'")
    sprite.go_to(0, 0)

def when_space_key_pressed():
    change_y_by(10)
    wait(0.5)
    change_y_by(-10)
