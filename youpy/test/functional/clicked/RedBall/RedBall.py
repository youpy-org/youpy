from youpy.code.english.everything import *

def when_program_start():
    go_to(point=Stage.center)
    while True:
        glide(2.5, to=Stage.pick_random_position())

def when_sprite_clicked():
    console.print("red ball clicked")
