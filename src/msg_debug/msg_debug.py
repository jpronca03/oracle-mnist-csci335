################################################################
# msg_debug.py
#   - Debugging tool for early development in python.
#
# New in v 0.4: 
#  * Added type-value (tvcheck, tvbcheck, ...) commands
#  * Added explicit testing commands (test, ptest) commands
#  * Revised documentation, renamed package
#
# New in v 0.3.2: New Debug class, log, assertions
#  * Methods now inside Debug class to simplify import & use
#  * Added log, methods to dump log to terminal or file
#  * check and pcheck methods now have optional third argument
#    for tests (statements tested using assertions)
#
# New in v0.3.1: DEBUG flag
#  * Allow messages to be skipped using a flag
#
# New in v0.3: DebugTimer
#  * Class to create objects to record labeled time stamps
#  * Use constructor to record/'start' timer
#  * Use 'check' and 'qcheck' to record duration from last
#    recorded time along with a label
#  * DebugTimer.check - prints msg at terminal
#  * DebugTimer.qcheck - ('quiet' check) record time without printing
#
# New in v0.2: 8 message types:
# * check, ncheck, dcheck, dncheck
# * pcheck, npcheck, dpcheck, dnpcheck
#
# Author: R. Zanibbi, Oct 2022, Mar 2023, Sept 2023, Nov 2023
################################################################

import time
import sys
import textwrap

##################################
# Function for error stream msgs
##################################
# Source: https://stackoverflow.com/questions/5574702/how-do-i-print-to-stderr-in-python
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


################################################################
# DebugTimer: Class for recording timing information with messages
# Please Note: Records wall-clock time, and not time running
#              on the processor.
################################################################
class DebugTimer:
    # Date and time string
    @staticmethod
    def date_str(time_secs):
        return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(time_secs))

    @staticmethod
    def entry_str(entry):
        (label, clock_time, duration) = entry
        return "{:>10.4f}s  {}".format(duration, label) + "\n"



    # Main data is a list of triples with a label, current clock time, and difference from
    # the previous entry in seconds
    def __init__(self, init_label="Timer"):
        self.entries = [(init_label, time.time(), 0)]

    # String summary of timing information + labels
    def __str__(self):
        head = self.entries[0]
        tail = self.entries[-1]

        # Report first label and start time
        out_string = "[ Timer: " + head[0] + " ]\n"
        out_string += "Started: " + DebugTimer.date_str(head[1]) + "\n"

        # Report start time and checkpoints
        out_string += "Total Duration: {:.4f} seconds".format(tail[1] - head[1]) + "\n"
        for i in range(1, len(self.entries)):
            out_string += DebugTimer.entry_str(self.entries[i])

        return out_string

    # Start again.
    def reset(self, start_label="Reset Timer"):
        self.entries = [(start_label, time.time(), 0)]

    # Add next time step with a label.
    # Optionally print last duration with timer name and message (single line)
    # 'vtcheck' for *verbose* time check
    def vtcheck(self, label="Check", show=True):
        last_time = self.entries[-1][1]
        current_time = time.time()
        self.entries.append((label, current_time, current_time - last_time))

        if show:
            head = self.entries[0]
            print(
                "[ Timer: " + head[0] + " ] " + DebugTimer.entry_str(self.entries[-1])
            )

    # Add next time step with a label, do *not* print a message
    def tcheck(self, qlabel="Check"):
        self.vtcheck(qlabel, False)


################################################################
# Debug module state
# * If 'state' is True, debug functions are executed, otherwise
#   all debug functions (check, pcheck, etc.) have no effect.
################################################################
class Debug:
    # Class attributes
    messages = __debug__ # UPDATE: set to python debug state
    exit_on_failed_test = False  # By default 'keep going.'

    # Debug data (times and message log)
    timer = DebugTimer("Debug Timer")
    log = ""

    ##################################
    # Turn debug messages on/off
    ##################################
    def msg_on():
        # Print messages, record to log
        Debug.messages = True

    def msg_off():
        # Do not print messages, do not record to log
        Debug.messages = False

    def exit_on_fail():
        Debug.exit_on_failed_test = True

    def no_exit_on_fail():
        Debug.exit_on_failed_test = False

    def reset_log():
        # Empty log, reset timer
        Debug.log = ""
        Debug.timer = DebugTimer("Debug Timer")

    ##################################
    # Dump log & times to standard out
    # or a file
    ##################################
    # Print times from timer object
    def show_times():
        if Debug.messages:
            print(str(Debug.timer))

    # Show log contents
    def show_log():
        print(Debug.log)

    # Dump state, times and log to file
    def dump_to_file(file_name="./Debug_log_and_times.txt"):
        with open(file_name, "w", encoding="utf-8") as file:
            file.write("[ Debug Log ]\n\n")
            file.write(f"Python __debug__: {__debug__}\n")
            file.write(f"Debug messages: {Debug.messages}\n")
            file.write(f"Exit on test fail: {Debug.exit_on_failed_test}\n\n")
            file.write(str(Debug.timer) + "\n")
            file.write("----------------------------------------\n")
            file.write("\n")
            file.write(Debug.log)

    # Dump state, times, and log to standard output or to file
    def dump(file_name=None):
        if file_name == None:
            print("[ Debug Log ]\n")
            print(f"Python __debug__: {__debug__}")
            print(f"Debug messages: {Debug.messages}")
            print(f"Exit on test fail: {Debug.exit_on_failed_test}\n")
            Debug.show_times()
            print("----------------------------------------")
            Debug.show_log()

        else:
            Debug.dump_to_file(file_name)

    ##################################
    # Timer operations
    ##################################
    # Record time stamp
    def time(qlabel="Check"):
        Debug.timer.tcheck(qlabel)

    # Record time stamp with command line output (verbose)
    def vtime(qlabel="Check", show=True):
        if not Debug.messages:
            # If messages disabled, no message.
            Debug.timer.vtcheck(qlabel, False)
        else:
            Debug.timer.vtcheck(qlabel, show)

    # Record time and pause; record initial time stamp, then stamp for pause
    def ptime(qlabel="Check & pause"):
        # Convenience method to create time stamp, create message and pause
        # without accidentally including pauses in the timing record.
        Debug.timer.tcheck( qlabel )

        # Check parameter to see whether we should pause.
        if Debug.messages and Debug.messages:
            Debug.pcheck('\n' + qlabel, 'time stamped, pausing.')
            Debug.timer.tcheck('   ( pause )')


    ##################################
    # 'check' messages
    #
    # Display message, expression, and
    #   optionally run a test as an
    #   assertion.
    ##################################
    def check(message, expression='', test=None, msg_start="[db.check]", pause=False,
              label=''): 
        
        if not Debug.messages:
        # If messages is turned off, do NOTHING for check commands.  This means
        # no command line messages OR log information.
            return

        out_string = ""
        exp_string = str(expression)
        type_string = str(type(expression))

        # Insert newline before expression if it contains a newline
        # (e.g., for 2D arrays)
        if '\n' in exp_string:
            exp_string = '\n' + exp_string + '\n'
            exp_string = textwrap.indent(exp_string, '  ')
        
        # Set first line of the message by message type
        # Hack: Insert label into message 'tab' at left if provided (e.g., fn name)
        if msg_start == "[db.check]":
            if label != '':
                msg_start= msg_start[:-1] + ': ' + label + ']'
            out_string = f"{msg_start} {message} : {exp_string}  ({type_string})"
        elif msg_start == "[db.msg]":
            if label != '':
                msg_start= msg_start[:-1] + ': ' + label + ']'
            out_string = f"{msg_start} {message}"
        else:
            # Test
            if label != '':
                msg_start= msg_start[:-1] + ': ' + label + ']'
            out_string = f"{msg_start} {message}:"

        # Add option to run a test/assertion
        failed = False
        if not test == None:
            try:
                assert test
                out_string += "\n  ++ Test PASSED"
            except:
                out_string += "\n  -- Test FAILED --"
                failed = True

        # Record message in log
        Debug.log += out_string + "\n"

        # Output message to standard or error stream,
        # exit program if failed test and exit flag set
        if failed and not Debug.exit_on_failed_test:
            # Write message to standard error
            eprint(out_string)

        elif failed and Debug.exit_on_failed_test:
            # Additional messages for exit;
            # Write to standard error
            exit_msg = "  >> Exiting program."
            Debug.log += exit_msg
            out_string += "\n" + exit_msg
            eprint(out_string)

            # Save log and timings by default if exiting
            Debug.dump_to_file()
            sys.exit(1)

        else:
            # Message to standard output
            print(out_string)

        # If needed, add pause message
        if pause:
            pause_msg = "  Press any key to continue...\n"
            Debug.log += pause_msg
            input(pause_msg)

    ##################################
    # Additional basic commands
    # (variations of 'check')
    ##################################
    def msg(message, label=''):
        Debug.check(message, msg_start="[db.msg]", label=label)

    def label(label):
        Debug.check('', msg_start="[db.msg]", label=label)

    def test(message, test_expr, label=''):
        Debug.check(message, test=test_expr, msg_start="[db.test]", label=label)

    ### With label annotation
    def msg_label(label, message):
        Debug.check(message, msg_start="[db.msg]", label=label)

    def check_label(label, message, expression, test=None):
        Debug.check(message, expression, test, label=label) 

    def test_label(label, message, test_expr):
        Debug.check(message, test=test_expr, msg_start="[db.test]", label=label)

    ##################################
    # Check messages WITH pause
    ##################################
    def pmsg(message, label=''):
        Debug.check(message, msg_start="[db.msg]", pause=True, label=label)
 
    def plabel(label):
        Debug.check('', msg_start="[db.msg]", label=label, pause=True)

    def pcheck(message, expression, test=None, label=''):
        Debug.check(message, expression, test, pause=True, label=label)

    def ptest(message, test_expr, label=''):
        Debug.check(message, test=test_expr, msg_start="[db.test]", pause=True, 
                    label=label)

    ### With label annotation
    def pmsg_label(label, message):
        Debug.check(message, msg_start="[db.msg]", pause=True, label=label)

    def pcheck_label(label, message, expression, test=None):
        Debug.check(message, expression, test, pause=True, label=label)
   
    def ptest_label(label, message, test_expr):
        Debug.check(message, test=test_expr, msg_start="[db.test]", pause=True, 
                    label=label)

################################################################
# TESTING
################################################################

def tests(dump_file_name):
    # Add time stamp
    Debug.time("first time stamp")

    # Check messages
    Debug.check("msg_check", (1, 2))
    Debug.pcheck("msg_pcheck", (1, 2))
    Debug.msg("msg")
    Debug.pmsg("pmsg")
    Debug.vtime("Check messages")  # Should produce output message

    # Run tests with assertion
    Debug.check("msg_test_check", (1, 2), (1 < 2) == True)
    Debug.pcheck("msg_test_pcheck", (1, 2), (1 < 2) == True)
    Debug.test("msg_test", (1 < 2) == True)
    Debug.ptest("msg_ptest", (1 < 2) == True)
    Debug.time("Valid tests")

    # Run tests with FAILING assertion
    # If exist_on_failed_test is True, only first command should be run, and
    #  default dump file written to disk.
    Debug.check("msg_test_check", (1, 2), (1 < 2) == False)
    Debug.pcheck("msg_test_pcheck", (1, 2), (1 < 2) == False)
    Debug.test("msg_test", (1 < 2) == False)
    Debug.test("msg_ptest", (1 < 2) == False)
    Debug.vtime("Invalid tests")  # Should produce output message

    # Output all log data, write to file
    Debug.dump()
    Debug.dump(dump_file_name)


# Unit test
#
# Have to test this interactively, checking outputs at the command line, and in the
# output files generated.
if __name__ == "__main__":
    # Message on, no exit on test assertion failure

    ##################################
    # Tests with messages, log
    ##################################
    print("*** MESSAGES ON ***")
    tests("db_tests_msg_on.txt")
    Debug.dump()

    ##################################
    # Turn off debug messages
    # - Log should not be updated,
    #   except for time stamps
    ##################################
    input("*** MESSAGES OFF ***")
    Debug.reset_log()
    Debug.msg_off()
    tests("db_tests_msg_off.txt")

    ##################################
    # Turn on exit on fail
    # * This will quite the program
    #   in the middle of the tests
    ##################################
    input("*** EXIT ON TEST FAIL ***")
    Debug.reset_log()
    Debug.msg_on()
    Debug.exit_on_fail()
    tests("db_tests_exit_on_fail.txt")
