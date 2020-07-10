from youpy.code.english.everything import *

def when_backdrop_switches_to_InGame():
    show()
    go_to(0, 0)
    point_in_direction(45)
    while True:
        move(10)
        if touching(scene.edge):
            y = y_position()
            if y < -150:
                switch_to("GameOver")
            elif y > 150:
                shared_variable.score += 1
            bounce()
        elif touching("Hand"):
            if direction() > 0:
                turn_counter_clockwise(90)
            else:
                turn_clockwise(90)

def when_backdrop_switches_to_GameOver():
    hide()
    stop_others()
    stop_it()

run(locals())
