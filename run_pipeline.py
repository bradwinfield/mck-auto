#!/usr/bin/env python3

import argparse
from errno import EEXIST
import importlib.util
import json
import os
import subprocess
import sys
import yaml

import pdb
#pdb.set_trace()
import pmsg
import interpolate
import merge_files

# CONSTANTS
vcenter_version = "7.0.3"

# This script will prepare an on-premise vSphere environment for 
# its first deployment of a TKGs workload cluster.

def dprint(msg):
    if verbose == True:
        pmsg.debug(msg)

def run_a_command(command):
    # Split up 'command' so it can be run with the subprocess.run method...
    pmsg.running (command)
    cmd_parts = command.split()
    returns = subprocess.run(cmd_parts)
    dprint("Command finished with exit code: " + str(returns.returncode))
    return returns.returncode

############################ Main ################################
# setup args...
help_text = "Run a a pipeline to setup a TKGs "+vcenter_version+" workload cluster on vSphere.\n"
help_text += "Examples:\n"
help_text += "./run_pipeline.py --help\n"

parser = argparse.ArgumentParser(description='Pipeline main script to deploy a TKGs workload cluster.')
parser.add_argument('-c', '--config_file', required=True, help='Name of yaml file which contains config params')
parser.add_argument('-d', '--dry_run', default=False, action='store_true', required=False, help='Just check things... do not make any changes.')
parser.add_argument('-v', '--verbose', default=False, action='store_true', required=False, help='Verbose output.')

args = parser.parse_args()
verbose = args.verbose
dry_run = args.dry_run

dry_run_flag = ""
if dry_run:
    dry_run_flag = " --dry_run"

verbose_flag = ""
if verbose:
    verbose_flag = " --verbose"

# Read configuration file.
if os.path.exists(args.config_file):
    with open(args.config_file, "r") as cf:
        try:
            configs = yaml.safe_load(cf)
        except yaml.YAMLError as exc:
            pmsg.fail(exc)
            exit (1)
else:
    pmsg.fail ("The config file does not exist. Please check the command line and try again.")
    exit(1)

# simpler variables
server = configs["vsphere_server"]
username = configs["vsphere_username"]
password = configs["vsphere_password"]
cluster = configs["cluster_name"]

# Check Pre-requisites
# 1. Need pyvmomi tools
if "pyVmomi" in sys.modules:
    dprint ("pyVmomi tools found in sys.modules.")
elif (spec := importlib.util.find_spec("pyVmomi")) is not None:
    dprint ("pyVmomi tools found using importlib.util.find_spec.")
else:
    pmsg.FAIL (" You need to install pyVmomi. See https://pypi.org/project/pyvmomi/ (or just run $ pip3 install --upgrade pyvmomi.)")
    exit (1)

###################### Step 1 ########################

###################### Done ########################
print ("")
pmsg.blue ("Done.")
