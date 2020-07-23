# Youpy

[![Last released version](https://img.shields.io/pypi/v/youpy.svg)](https://pypi.org/project/youpy)
[![Supported python versions](https://img.shields.io/pypi/pyversions/youpy.svg)](https://pypi.org/project/youpy/)
[![Package stability](https://img.shields.io/pypi/status/youpy.svg)](https://pypi.org/project/youpy/)
[![License](https://img.shields.io/pypi/l/youpy.svg)](https://pypi.org/project/youpy/)

Youpy aims at smoothing Python learning curve for beginners with or without
knowledge of [Scratch](https://scratch.mit.edu/). It does this by
providing a simple game engine framework
and a front-end API as close as possible to Scratch.

Many beginners guide for Python only offers command line activities
based on the austere interfaces supported by the `input` and `print`
function. On the contrary, Youpy brings a modern graphical API allowing
teachers to create rich recreational activities for education purpose
accessible to student with no programming skills.

Imagine a simple game represented by the following screenshot, where
the player control the "Hand" sprite at the bottom of the stage to
catch the bouncing ball sprite. The player scores one point each time the
ball touches the top edge and loses when the ball touches the bottom
edge.

![BallBar screenshot](doc/ballbar-screenshot.png)

Part of the code of Basketball sprite can be translated from Scratch
to Python using Youpy, like this:

![Scratch VS Youpy's code](doc/code-example.png)

Youpy's goals:
- Make beginners enjoy programming in Python as much as in Scratch
- Stick to plain Python code with less implicit magic possible.

Youpy's explicit non-goals:
- No 3D: 2D is enough for beginners
- Fast rendering: we only need to handle a handful of a hundred
  sprites at most

## Table of contents

1. [Install/upgrade procedure](INSTALL.md)
1. [Youpy's project examples](EXAMPLES.md)
1. [Scratch functions implementation status](SCRATCH.md)
1. [Developers guide](HACKING.md)

## License

Youpy is release under the term of the [BSD 3-Clause license](LICENSE.txt)
Copyright (c) 2020, Nicolas Desprès
All rights reserved.
