# How to run Youpy's examples

Youpy's comes with multiple examples available in the `youpy.examples`
package. It exists various way to run an example. Before to run one
make sure you have [installed](INSTALL.md) Youpy properly.

## Embedded examples

You can get a list of available examples by running in an interactive
Python session:

```python
from youpy.examples import list_example_names
list_example_names()
```

Then follow this procedure for running an example:

1. Using the Terminal, you can just type:
   ```bash
   python -m youpy.examples.SimpleBasketBall
   ```
1. Using the Thonny IDE, you can run in the console:
   ```python
   from youpy.examples import run_example
   run_example("SimpleBasketBall")
   ```

## Third-party examples

Alternatively, you extract the examples from
Youpy's [source zip archive](https://pypi.org/project/youpy/#files) or
download any other Youpy's project.

You can run a Youpy's project like this from the Terminal:
```bash
python -m youpy run <path/to/example/directory>
```

Or, by opening one of the script of the project in Thonny and then
click the "run" button.
