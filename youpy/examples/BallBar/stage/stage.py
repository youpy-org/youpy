from youpy.code.english.everything import *

def when_program_start():
    console.print("program is starting")
    shared_variable.score = 1
    shared_variable.score.hide()
    switch_backdrop_to("Welcome")
    console.print("done initializing the program")

def when_space_key_pressed():
    shared_variable.score.show()
    switch_backdrop_to("InGame")

run(locals())
