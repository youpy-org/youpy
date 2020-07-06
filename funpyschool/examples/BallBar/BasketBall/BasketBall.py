from funpyschool.functions.all import *

def when_backdrop_switches_to_InGame():
    show()
    go_to(0, 0)
    point_in_direction(45)
    while True:
        move(10)
        if y_position() < -150 and touching(screen.edge):
            switch_to(backdrop.GameOver)
            variable.score += 1
            if touching(sprite.Hand):
                if direction() > 0:
                    turn_counter_clockwise(90)
                else:
                    turn_clockwise(90)
        if on_edge():
            bounce()

def when_backdrop_switches_to_GameOver():
    hide()
    stop_others()
    stop_it()
