#!/usr/bin/env python3

# General purpose python functions

import os
import subprocess
import pmsg
import re
import time
# import pdb

class helper():
    """
    Class used to provide general purpose python functions.
    """


env_override_file = "/tmp/env_override_file"


# ########################################################
def __init__(self):
    pass


# ########################################################
def run_a_command_list(command):
    """
    :param command: List of command and all its arguments.
    :returns: Integer - Returns the number of errors the command caused.
    :rtype: int
    """

    # Split up 'command' so it can be run with the subprocess.run method...
    myenv = dict(os.environ)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=myenv)
    output, err = process.communicate()
    if err is not None:
        return 1
    return 0


# ########################################################
def run_a_command(command):
    """
    :param command: String of command and all its arguments.
    :returns: Integer - Returns the number of errors the command caused.
    :rtype: int
    """

    # Split up 'command' so it can be run with the subprocess.run method...
    pmsg.running(command)
    cmd_parts = command.split()
    myenv = dict(os.environ)
    returns = subprocess.run(cmd_parts, env=myenv)
    return returns.returncode

#############################################################
def run_a_command_get_stdout(command_and_args_list):
    tlines = []
    process = subprocess.Popen(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    # Split up the lines and decode each line and remove newlines...
    if output is not None:
        lines = output.splitlines()
        for line in lines:
            tlines.append(line.decode('utf-8').strip())

    return tlines


#############################################################
def check_for_result(command_and_args_list, expression):
    """Checks to see if a given command returns an expected value.

    Args:
        command_and_args_list (list): Run this command with arguments and capture the output.
        expression (string): Split the result of the command into lines and see if any line matches this expression.
    :returns: Boolean - Match or no match
    :rtype: Boolean
    """

    # Run the command capturing the stdout
    process = subprocess.Popen(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    lines = output.splitlines()
    for line in lines:
        if re.search(expression, line.decode("utf-8")) is not None:
            return True
    return False

def add_env_override(newfile, varname, value):
    """ Create (if newfile=True) or add to the environment override file and put the varname and value in it.

    Args:
        newfile (Boolean): create a new override file if True. Otherwise just add a new line to it.
        varname (string): name of environment variable to set (export).
        value (string): value of variable.
    :returns: Boolean - writing to envirnment override file success.
    :rtype: Boolean
    """
    openflag = 'a'
    if newfile:
        openflag = 'w'
    with open(env_override_file, openflag) as env_file:
        env_file.write(varname + ": \"" + value + "\"\n")


def check_for_result_for_a_time(command_and_args_list, expression, check_how_often, max_checks):
    """
    Run a command with arguments and check the output for a specific string of text (regular expression) over a time period.

    Args:
        command_and_args_list (list): Run this command with arguments and capture the output.
        expression (string): Split the result of the command into lines and see if any line matches this expression.
        check_how_often (int): check every <check_how_often> seconds for the expression.
        max_checks (int): check a maxiumum of this many times before giving up.

    :returns: Boolean - Match or no match
    :rtype: Boolean

    """
    found = False
    for i in range(max_checks):
        if check_for_result(command_and_args_list, expression):
            found = True
            break
        time.sleep(check_how_often)

    return found
