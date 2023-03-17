#!/usr/bin/env python3

# General purpose python functions

import os
import subprocess
import pmsg


class helper():
    """
    Class used to provide general purpose python functions.
    """


# ########################################################
def __init__(self):
    pass


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
