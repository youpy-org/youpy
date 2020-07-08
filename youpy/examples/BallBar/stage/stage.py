from youpy.code.english.everything import *

def when_program_start():
    shared_variable.score = 1
    shared_variable.score.hide()
    switch_to("Welcome")

def when_space_key_pressed():
    shared_variable.score.show()
    switch_to("InGame")

run(locals())
