from youpy.code.english.everything import *

def when_program_start():
    shared_variable.score = 1
    shared_variable.score.hide()
    switch_backdrop_to("Welcome")

def when_space_key_pressed():
    shared_variable.score.show()
    switch_backdrop_to("InGame")

run(locals())
