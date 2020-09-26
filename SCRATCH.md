# Scratch's functions development status

This section describe the status of Scratch block implementation in
Youpy. It can also serves as a handbook for quickly finding the
Youpy's way to do things.

## Motion

Motion features may be found in `youpy.code.<language>.motion`

| Block | Implementation | Documented |
| ----- | -------------- | ---------- |
| move | `move` Youpy's function | no |
| turn clockwise | `turn_clockwise` Youpy's function | no |
| turn counter_clockwise | `turn_counter_clockwise` Youpy's function | no |
| go to random position | `go_to` with `point=Stage.random_position` | no |
| go to mouse-pointer | `go_to` with `point=Mouse.position` | no |
| go to sprite position | `go_to_sprite` Youpy's function | no |
| go to (x, y) | `go_to(x, y)` Youpy's function | no |
| glide N secs to random position | `glide` with `to=Stage.random_position` | no |
| glide N secs to mouse-pointer | `glide` with `to=Mouse.position` | no |
| glide N secs to sprite position | `glide` with `to="sprite name"` | no |
| glide N secs to (x, y) | `glide` Youpy's function | no |
| point in direction | `point_in_direction` Youpy's function  | no |
| point towards mouse-pointer | not implemented yet | no |
| point towards sprite | not implemented yet | no |
| change x by | `change_x_by` Youpy's function | no |
| set x to | `set_x_to` Youpy's function | no |
| change y by | `change_y_by` Youpy's function | no |
| set y to | `set_y_to` Youpy's function | no |
| if on edge, bounce | `bounce_if_on_edge` Youpy's function | no |
| x position value | `x_position` Youpy's function | no |
| y position value | `y_position` Youpy's function | no |
| direction value | `direction` Youpy's function | no |
| set rotation style | not implemented yet | no |
| show x position | not implemented yet | no |
| show y position | not implemented yet | no |
| show direction | not implemented yet | no |

## Looks

Looks features may be found in `youpy.code.<language>.looks`

| Block | Implementation | Documented |
| ----- | -------------- | ---------- |
| say something for N seconds | not implemented yet | no |
| say something | not implemented yet | no |
| think something for N seconds | not implemented yet | no |
| thing something | not implemented yet | no |
| switch costume to | not implemented yet | no |
| next costume | not implemented yet | no |
| switch backdrop to | `switch_backdrop_to` Youpy's function | no |
| switch backdrop to and wait| not implemented yet | no |
| next backdrop | not implemented yet | no |
| change size by | not implemented yet | no |
| set size by | not implemented yet | no |
| change effect by | not implemented yet | no |
| set effect by | not implemented yet | no |
| clear graphics effect | not implemented yet | no |
| show | `show` Youpy's function | no |
| hide | `hide` Youpy's function | no |
| go to layer | not implemented yet | no |
| go forward/backward N layer | not implemented yet | no |
| costume number/name | not implemented yet | no |
| backdrop number/name | not implemented yet | no |
| size value | not implemented yet | no |
| show costume number/name | not implemented yet | no |
| show backdrop number/name | not implemented yet | no |
| show size value | not implemented yet | no |

## Sounds

Sound features may be found in `youpy.code.<language>.sound`

| Block | Implementation | Documented |
| ----- | -------------- | ---------- |
| play sound until done | not implemented yet | no |
| start sound | not implemented yet | no |
| stop all sounds | not implemented yet | no |
| change effect | not implemented yet | no |
| set effect | not implemented yet | no |
| clear sound effect | not implemented yet | no |
| change volume by | not implemented yet | no |
| set volume to | not implemented yet | no |
| volume value | not implemented yet | no |
| show volume value | not implemented yet | no |

## Events

Events are implemented as callback method following a naming
convention (function name starting by `when_`).

| Block | Implementation | Documented |
| ----- | -------------- | ---------- |
| when green flag clicked | `when_program_start` | no |
| when key pressed | `when_<key>_key_pressed` | no |
| when stage clicked | not implemented yet | no |
| when this sprite clicked | not implemented yet | no |
| when backdrop switches to | `when_backdrop_switches_to_` | no |
| when loudness | not implemented yet | no |
| when timer | not implemented yet | no |
| when I receive message | not implemented yet | no |
| broadcast message | not implemented yet | no |
| broadcast message and wait | not implemented yet | no |

## Control

Most features found in Scratch's control panel are implemented as
Python statements. Other functions may be found in
`youpy.code.<language>.control`.

| Block | Implementation | Documented |
| ----- | -------------- | ---------- |
| wait | `youpy.control.wait` function | no |
| repeat | `for in range` | no |
| forever | `while True` | no |
| if-then | `if` statement | no |
| if-then-else | `if-else` statement | no |
| wait until | not implemented yet | no |
| repeat until | `while not` statement | no |
| stop all | not implemented yet | no |
| stop this script | `youpy.control.stop` function | no |
| stop other scripts in sprite | not implemented yet | no |
| create clone of | not implemented yet | no |

## Sensing

Sensing features may be found in `youpy.code.<language>.sensing`

| Block | Implementation | Documented |
| ----- | -------------- | ---------- |
| touching edge | `touching(scene.edge)` | no |
| touching sprite | `touching("SpriteName")` | no |
| touching mouse-pointer | not implemented yet | no |
| touching color | not implemented yet | no |
| color is touching | not implemented yet | no |
| distance to mouse-pointer | not implemented yet | no |
| distance to sprite | not implemented yet | no |
| ask and wait | not implemented yet | no |
| key pressed? | not implemented yet | no |
| mouse down?  | `if Mouse.down` | no |
| mouse x      | `Mouse.x` | no |
| mouse y      | `Mouse.y` | no |
| set drag mode | not implemented yet | no |
| loudness value | not implemented yet | no |
| show loudness value | not implemented yet | no |
| timer        | not implemented yet | no |
| reset timer  | not implemented yet | no |
| timer value | not implemented yet | no |
| show timer value | not implemented yet | no |
| current year/month/... value | not implemented yet | no |
| show current year/month/... value | not implemented yet | no |
| current year/month/... | use standard datetime or time module | no |
| days since 2000 | not implemented yet | no |
| username value | not implemented yet | no |
| show username value | not implemented yet | no |

## Operators

Most features found in Scratch's operators panel are implemented as
Python operators. Other functions may be found in
`youpy.code.<language>.operators`.

| Block | Implementation | Documented |
| ----- | -------------- | ---------- |
| `+` | `+` opeartor | no |
| `-` | `-` opeartor | no |
| `*` | `*` opeartor | no |
| `/` | `/` opeartor | no |
| pick random | `random.randint` | no |
| `>` | `>`  operator | no |
| `<` | `<`  operator | no |
| `=` | `==` operator  | no |
| `and` | `and` operator | no |
| `or`  | `or`  operator | no |
| `not` | `not` operator | no |
| `join` | `+` operator on `str` | no |
| `letter` | `[]` operator on `str` | no |
| `lenght of `| `len` built-in function | no |
| `contains` | `in` operator on `str` | no |
| `mod` | `%` operator  | no |
| `round` | `round` built-in function | no |
| `abs` | `abs` built-in function | no |
| `floor` | `math.floor` function | no |
| `ceiling` | `math.ceil` function | no |
| `sqrt` | `math.sqrt`  function | no |
| `sin`  | `math.sin`   function | no |
| `cos`  | `math.cos`   function | no |
| `tan`  | `math.tan`   function | no |
| `asin` | `math.asin`  function | no |
| `acos` | `math.acos`  function | no |
| `atan` | `math.atan`  function | no |
| `ln`   | `math.log`   function | no |
| `log`  | `math.log10` function | no |
| `e^`   | `math.exp`   function | no |
| `10^`  | use built-in scientific notation | no |

## Variables

Variables features may be found in `youpy.code.<language>.variables`

| Block | Implementation | Documented |
| ----- | -------------- | ---------- |
| show variable value | implemented without the same look'n feel | no |
| set    | using assignment operator | no |
| change | using `+=` operator only | no |
| show   | yes | no |
| hide   | yes | no |

## My Blocks

Already implemented as Python function.

# Differences with Scratch

## Variable

- Named `SharedVariable` to distinguish with Python's variables that
  might be local or global.
- They must be assigned once before first use (in Scratch
  you create it in the GUI).
- They can be of any type.

## Events

Events in Youpy are implemented as callback function following a
naming convention. It has some drawbacks.

- You can only have one function of the same name in the same
  module. This is due to Python name binding. If you define a
  variable or a function with the name twice the second definition
  overwrite the first one. Thus, you can have only one
  `when_program_start` event per sprite. Whereas in Scratch you may
  provide multiple script triggered on this event. The common
  workaround is define two functions and call them in the event
  handler. You will lose parallelism but in most cases it does not matter.
