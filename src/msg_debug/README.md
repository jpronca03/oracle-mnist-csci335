# Message-Oriented Debugging Library for Python (`msg_debug`)

**Author:** R. Zanibbi (rxzvcs@rit.edu)<br>
**Date:** November, 2023 <br>
**Version:** 0.4<br>
**License:** GPL v0.3 (see LICENSE file)

## Overview: Yet Another Debugging Library -- Why?

`msg_debug` provides short commands for creating readable debugging messages,
to avoid repeatedly adding and removing `print`, `input`, and `assert`
statements in the early stages of creating a program. At this early stage, our
understanding of the program requirements tend to change frequently, and many small-scale tests are needed to insure that things operate as intended through these changes (e.g., that variables are of expected type/value, have values/shapes of specific sizes, etc.).

A small set of functions run tests with associated *descriptive messages*,
which act as annotations (e.g., to describe where or why a debug message is
produced in debug output).  In addition to making it easier to see the purpose
of tests in debug output, these descriptive messages double as annotations to
make finding individual tests in code easier (e.g., using `Ctrl-f`, `grep`, or
text editor/IDE search functions).  Debug messages may be started/stopped at
any point in a program.  

The library also supports recording and reporting time stamps within a
formatted table, as a way to quickly profile as-you-go.  Timing information is collected and reportable *independently*
from the debug message state.

While the library is designed to avoid invoking debuggers or profilers, `msg_debug` is intended to complement rather
than replace standard debuggers and profilers in the early stages of software
development.

Descriptions and examples of using the operations in the library are provided below.

## Simple Debug Messages

Simple text messages are useful when printing out basic information and liveness messages (e.g., to show that a program reaches a location in a script or function). 

To print a text message, a message *label*, or a text message with a label, use the following (`msg` and `label` are strings):

```
db.msg(msg)
db.label(label)
db.msg_label(label, msg)
```

All simple debug messages are printed with the label `[db.msg]`. Commands with a `label` annotate the label with a suffix  (e.g., `[db.msg: my_function()]`).


**Pausing:** Adding a `p`  before each message command name above will pause for a key press (e.g., `db.pmsg`, `db.plabel`, `db.pmsg_label`).



### Examples: Simple Messages 


```
>>> from msg_debug import Debug as db
>>> db.msg('In here')
[db.msg] In here
>>> db.label('my_function()')
[db.msg: my_function()] 
>>> db.msg_label('my_function()', 'In here')
[db.msg: my_function()] In here
>>> db.pmsg('In here')
[db.msg] In here
  Press any key to continue...
>>> db.pmsg_label('HERE', 'In here')
[db.msg: HERE] In here
  Press any key to continue...
>>> db.plabel('THERE')
[db.msg: THERE] 
  Press any key to continue...
>>> 
```





## Checking Expressions and Running Tests

Often we want to check the type and value of variables or expressions, and run tests. The library provides functions for this, which produce the label `[db.check]` for checking values/expressions, and `[db.test]` for tests.

To **check the type and value** of a variable or expression, optionally with a message label annotation, use:

```
db.check(msg, expression)
db.check_label(label, msg, expression)
```

To **run a test** given as a boolean expression, you can use one of:

```
db.test(msg, bool_test_expression)
db.test_label(label, msg, bool_test_expression)
```

**Pausing**. Adding `p` at the front of the function names above will also pause the program.


### Examples: Type/Value Checks and Tests

In the example below, we import the library, and then check and test both integer and array values/properties using the `db.check()` and `db.test()` functions. 

This example also illustrates variations of these commands that annotate message labels (e.g., `db.check_label()`), pause the program (e.g., `db.ptest()`) or both (e.g., `db.ptest_label()`).

```
>>> from msg_debug import Debug as db
>>> import numpy as np
>>> x = 5
>>> z = np.array([[1,2],[3,4]])
>>> 
>>> # Checking values
>>> db.check('Checking x', x)
[db.check] Checking x : 5  (<class 'int'>)
>>> db.check('Checking z', z)
[db.check] Checking z : 
  [[1 2]
   [3 4]]
  (<class 'numpy.ndarray'>)
>>> # Check with annoted message label 
>>> db.check_label('my_function()', 'Checking x', x)
[db.check: my_function()] Checking x : 5  (<class 'int'>)
>>>
>>> # Running Tests  
>>> db.test('x < 5', x < 5)
[db.test] x < 5:
  -- Test FAILED --
>>> db.test_label('HERE', 'Checking x is 5', x == 5)
[db.test: HERE] Checking x is 5:
  ++ Test PASSED
>>> db.ptest_label('THERE', 'Checking z shape', np.shape(z) == (2,2))
[db.test: THERE] Checking z shape:
  ++ Test PASSED
  Press any key to continue...
>>>
```

**Seeing boolean test statements in messages.** To see boolean tests in debug messages, include it in the text message string. For example:

```
>>> x = 2
>>> db.test('Testing x > 1', x>1)
[db.test] Testing x > 1:
  ++ Test PASSED
>>> 
```

**Exiting on test failure.** If you want your program to exit if a test fails, you can use `db.exit_on_fail()`. 

```
>>> db.exit_on_fail()
>>> x = 5
>>> db.test('x > 10', x > 10)
[db.test] x > 10:
  -- Test FAILED --
  >> Exiting program.
```

After seeing the final message above, python will exit back to the command line.

*Note:* If needed, the function `db.no_exit_on_fail()` can set a program back to the default behavior, where failed tests do not exit the program.

## Timing Your Program

Immediately after importing the debug library, a timer is started. Commands may
be used to record labels associated with time stamps in the timer (similar to a
stopwatch with an option to record multiple times).

Key operations:

* `db.time(label_str)` records timestamps with a label
* `db.vtime(<str>)` ('verbose') output timing info as well as update timestamps
* `db.ptime(label_str)` will record a timestamp and then pause.<br>Two timestamps are created: one before the pause, and one after the pause labeled `( pause)`
* `db.show_times()` displays all timed checkpoints and total time


The timer is helpful for capturing timing data directly within a program.

 
### Examples: Using Timestamps

Here is an example of using timestamps to record durations. In an actual program, these timestamps may be defined within any function in any file where the `Debug` class has been imported as `db` (i.e., at the beginning of the import statements).

Times are reported in terms of **total duration**, and the time taken to the first timestamp from when the timer was started, and then each subsequent timestamp requested in the program (see below).

`db.ptime(msg, True)` is useful when we want to record execution time at a point and then pause: this records the time taken to pause separately, as seen below. 

```
>>> from msg_debug import Debug as db
>>> db.time('first timestamp')
>>> db.time('second timestamp')
>>> x = 2
>>> y = 3
>>> z = x*y
>>> db.ptime('third timestamp')

third timestamp : time stamped, pausing.
Press any key to continue...
>>> db.vtime('final timestamp')
[ Timer: Debug Timer ]    11.6336s  final timestamp

>>> db.show_times()
[ Timer: Debug Timer ]
Started: Sat, 25 Nov 2023 17:17:46
Total Duration: 61.9447 seconds
    5.5321s  first timestamp
    6.3011s  second timestamp
   36.0928s  third timestamp
    2.3852s     ( pause )
   11.6336s  final timestamp
>>> 
```
 
## Turning Messages On/Off and Viewing/Saving the Log 
 
**Turning messages off.** By default, the library turns messages off if the built-in `__debug__` variable is `False` (e.g., when running Python with the 'optimize' flag, `python -O`). This allows the tool to be consistent with the built-in python debugger (pdb).

When messages are turned off, no messages or tests are run or
recorded. **Note: Timing information is still collected** and can be reported even when messages are turned off. 

To explicitly stop and start messages at the command line and in the log:

* `db.msg_off()` turns off debug messages 
* `db.msg_on()` turns on debug messages 


**Viewing & Saving the Log.** You can view current timing and generated messages using:

```
db.dump()
``` 

or save the log to a file `debug_log.txt` using:

```
db.dump('debug_log.txt')
```

The log shows information on the debugger state, timing information, and 
*all* `check` and `test` commands run during the program.

### Example: Viewing and Saving the Debug Log

This example generates debug statements, and then prints the contents of the debug log where they are stored to the command line.

Note that the times shown are the total time, followed by the time since the start or previous timestamp for each labeled entry in the timer output.

```
>>> from msg_debug import Debug as db
>>> x = 5
>>> db.msg_label('Here', 'Greetings!')
[db.msg: Here] Greetings!
>>> db.time('First timestamp')
>>> db.check('x is', x)
[db.check] x is : 5  (<class 'int'>)
>>> db.test('x < 5', x<5)
[db.test] x < 5:
  -- Test FAILED --
>>> db.vtime('Second timestamp')
[ Timer: Debug Timer ]    27.1137s  Second timestamp

>>> db.dump()
[ Debug Log ]

Python __debug__: True
Debug messages: True
Exit on test fail: False

[ Timer: Debug Timer ]
Started: Mon, 27 Nov 2023 11:57:39
Total Duration: 57.7066 seconds
   30.5930s  First timestamp
   27.1137s  Second timestamp

----------------------------------------
[db.msg: Here] Greetings!
[db.check] x is : 5  (<class 'int'>)
[db.test] x < 5:
  -- Test FAILED --

>>> 
```

**Saving the log to a file.**  If `db.dump()` is passed a file name, the debug log in the same format as shown above is written to the file indicated.


## Acknowledgements & Author Information

My thanks to the students in my machine learning and information retrieval
courses in 2022-2023, and the Document and Pattern Recognition Lab at the
Rochester Institute of Technology (RIT, USA), who provided feedback on earlier
versions of the library.

### Author Information

If you have questions, please contact the author via email at 
<a href="mailto:rxzvcs@rit.edu">rxzvcs@rit.edu</a>.

<pre>
Richard Zanibbi
Director, Document and Pattern Recognition Lab (dprl)
Professor, Department of Computer Science
Rochester Institute of Technology, NY, USA
Web: www.cs.rit.edu/~rlaz
</pre>

