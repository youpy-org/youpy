How to run Youpy's examples
------------------------------

Youpy's comes with multiple examples available in the `youpy.examples`
package. It exists various way to run an example. Before to run one
make sure you have [installed](INSTALL.md) Youpy properly.

You can get a list of available examples by running in an interactive
Python session:

```python
from youpy.examples import list_example_names
print(list_example_names())
```

Then follow this procedure for running an example:

1. Using the Terminal, you can just type:
   ```bash
   python -m youpy.examples.BallBar
   ```
1. Using the Thonny IDE, you can run in the console:
   ```python
   from youpy.examples import run_example
   run_example("BallBar")
   ```
