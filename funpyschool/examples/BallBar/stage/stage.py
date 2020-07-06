from funpyschool.functions.all import *

def when_game_start():
    hide_variable(variable.score)
    switch_to(backdrop.Welcome)

def when_space_key_pressed():
    variable.score = 1
    variable.score.show()
    backdrop.InGame.switch_to()
