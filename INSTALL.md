# How to install Youpy

This document presents the various methods available to install youpy
on your machine.

## Install from command-line interface
### Windows
1. Install a compatible version of the Python
   interpreter
   [![Supported python versions](https://img.shields.io/pypi/pyversions/youpy.svg)](https://pypi.org/project/youpy/)
   by downloading
   an [executable installer](https://www.python.org/downloads/windows/)
1. Choose custom installation and tick the following boxes:
   - "pip"
   - "Add Python to program PATH"
1. Start the command prompt by pressing `Windows+R`, then typing `cmd`
   and finally pressing `RETURN`.
1. From the command prompt type:
   ```
   python -m pip install youpy
   ```

### macOS
1. Install a compatible version of the Python interpreter [![Supported python versions](https://img.shields.io/pypi/pyversions/youpy.svg)](https://pypi.org/project/youpy/)
    ```bash
    brew install python
    ```

1. Youpy uses [pygame](https://pygame.org) behind the scene. If no
   wheel package is available, pip may compile it from source. In such
   case, you'll need to install the sdl library
    ```bash
    brew install sdl sdl2
    ```

1. Install Youpy
    ```bash
    python3 -m pip install youpy
    ```

## Install in Thonny

[Thonny](https://thonny.org) is Python IDE for beginners which comes
with an embedded Python interpreter.

1. You can either configure Thonny to use the system-wide python
   interpreter if you have one installed, or use the embedded interpreter
   (default). You choose between one of these options by opening the
   preference dialog box and selecting the interpreter pane.
1. Install youpy by using the package manager available in the `Tools`
   menu.
