#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""Multi-processing version.
"""

# TODO: Test without lock at all just by passing messages (i.e. to get the
#       mouse cursor position, it must sends a message to query it)


import sys
import argparse
import multiprocessing
from dataclasses import dataclass
from typing import Tuple
from random import randint
import time
import functools

COLOR_BLACK  = (  0,   0,   0)
COLOR_WHITE  = (255, 255, 255)
COLOR_GRAY   = (128, 128, 128)
COLOR_RED    = (255,   0,   0)
COLOR_GREEN  = (  0, 255,   0)
COLOR_BLUE   = (  0,   0, 255)
COLOR_YELLOW = (  0, 255, 255)
COLOR_PURPLE = (255,   0, 255)
COLORS = (
    COLOR_BLACK ,
    COLOR_WHITE ,
    COLOR_GRAY  ,
    COLOR_RED   ,
    COLOR_GREEN ,
    COLOR_BLUE  ,
    COLOR_YELLOW,
    COLOR_PURPLE,
)

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

class FrequencyMeter:

    def __init__(self):
        self._count = 0
        self._frequency = 0.0
        self._last_updated_at = 0.0
        self._updated = False

    def update(self):
        t = time.time()
        duration = (t - self._last_updated_at)
        if duration > 1.0: # sec
            self._frequency = self._count / duration
            self._count = 0
            self._last_updated_at = t
            self._updated = True
        else:
            self._count += 1
            self._updated = False
        return self._updated

    @property
    def frequency(self):
        return self._frequency

    @property
    def updated(self):
        return self._updated

    def __str__(self):
        return f"{self._frequency:.2f}"

    def __repr__(self):
        return f"{self.__class__.__name__}(count={self.count}, "\
            f"frequency={self._frequency}, "\
            f"last_updated_at={self._last_updated_at})"

class Sprite:

    RADIUS = 5

    def __init__(self, x=0, y=0, color=None):
        self.x = x
        self.y = y
        self.color = color
        # self._action_q = threading.local.action_queue
        # self._reply_q = threading.local.reply_queue
        # self._action_q.put(SpriteCreate(color=self.color,
        #                                 x=self.x,
        #                                 y=self.y))
        # self._id = self._reply_q.get()

    @property
    def position(self):
        return (self.x, self.y)

    def move(self, dx, dy):
        pass

class Mouse:

    def __init__(self, _synced_list):
        self._synced_list = _synced_list

    def _set_pos(self, x, y):
        self._synced_list[0] = x
        self._synced_list[1] = y

    @property
    def x(self):
        return self._synced_list[0]

    @property
    def y(self):
        return self._synced_list[1]

    def __str__(self):
        return f"{self.__class__.__name__}(x={self.x}, y={self.y})"

@dataclass
class SpriteMove:
    dx: int
    dy: int

class ACK:
    pass

class END:
    pass

class StopUserScript(Exception):
    pass

class UserScript(multiprocessing.Process):

    def __init__(self, sprite, num, direction=1, pipe=None,
                 mouse=None, start_event=None):
        super().__init__(name=f"Sprite{id(sprite)}")
        self.sprite = sprite
        self.num = num
        self.direction = direction
        self._action_q, self._reply_q = pipe
        self.mouse = mouse
        self.start_event = start_event

    def run(self):
        self.start_event.wait()
        try:
            self.user_run()
        except StopUserScript:
            return

    def user_run(self):
        direction = self.direction
        while True:
            for _ in range(80):
                # self.mouse.x + self.mouse.y # explicitly access mouse at each step
                obj = SpriteMove(direction * 10, 0)
                self._action_q.put(obj)
                ans = self._reply_q.get()
                if isinstance(ans, ACK):
                    pass
                elif isinstance(ans, END):
                    raise StopUserScript
                # if self.num == 0:
                #     sum(range(1000000))
                if self.num == 0:
                    while True:
                        pass
                # if self.num == 0:
                #     raise RuntimeError('intentional error')
            direction = 1 if direction < 0 else -1

def render(sprites, pipes, mouse, start_event):
    import pygame
    pygame.init()
    pygame.display.set_caption('FunPySchool')
    screen = pygame.display.set_mode(SCREEN_SIZE)
    mouse._set_pos(*pygame.mouse.get_pos())
    print("mouse", mouse)

    fps = FrequencyMeter()
    def paint():
        screen.fill(COLOR_BLACK)
        for sprite in sprites:
            pygame.draw.circle(screen, sprite.color, (sprite.position),
                               sprite.RADIUS)
        if fps.update():
            print(fps)
        pygame.display.flip()

    paint()
    is_running = True
    start_event.set()
    while is_running:
        for event in pygame.event.get():
            # print(event)
            # print(type(event))
            if event.type == pygame.QUIT \
               or (event.type == pygame.KEYUP
                   and event.key == pygame.K_ESCAPE):
                is_running = False
            elif event.type == pygame.MOUSEMOTION:
                mouse._set_pos(*event.pos)
        for i, (action_q, reply_q) in enumerate(pipes):
            if not action_q.empty():
                action = action_q.get()
                if isinstance(action, SpriteMove):
                    sprites[i].x += action.dx
                    sprites[i].y += action.dy
                else:
                    raise RuntimeError(f"unhandled action '{action}'")
                reply_q.put(ACK())
        paint()
    for _, reply_q in pipes:
        reply_q.put(END())
    print("render end")

def build_cli():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-j", "--njobs",
        action="store",
        type=int,
        default=1,
        help="A description.")
    return parser

def main(argv):
    cli = build_cli()
    options = cli.parse_args(argv[1:])
    with multiprocessing.Manager() as manager:
        start_event = manager.Event()
        mouse = Mouse(manager.list([None, None]))
        pipes = [(manager.Queue(), manager.Queue())
                 for i in range(options.njobs)]
        sprites = [Sprite(x=((i*10)//SCREEN_HEIGHT)*50, y=(i*10)%SCREEN_HEIGHT,
                          color=COLORS[(i%(len(COLORS)-1))+1])
                   for i in range(options.njobs)]
        user_scripts = [UserScript(sprites[i], i,
                                   direction=1,
                                   pipe=pipes[i],
                                   mouse=mouse,
                                   start_event=start_event)
                        for i in range(options.njobs)]
        for i in user_scripts:
            i.start()
        render(sprites, pipes, mouse, start_event)
        for i in user_scripts:
            i.join()
        print("ciao")
        return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
