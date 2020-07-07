from youpy.code.english.everything import *

def when_program_start():
    shared_variable.score = 1
    hide_variable(shared_variable.score)
    switch_to(backdrop.Welcome)

def when_space_key_pressed():
    shared_variable.score.show()
    backdrops.InGame.switch_to()

run(locals())
