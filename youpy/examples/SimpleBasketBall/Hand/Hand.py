from youpy.code.english.everything import *

def when_backdrop_switches_to_InGame():
    go_to(0, -160)
    show()

def when_right_arrow_key_pressed():
    move(10)

def when_left_arrow_key_pressed():
    move(-10)

def when_backdrop_switches_to_GameOver():
    hide()
    # stop_others()
    stop()

run(locals())
