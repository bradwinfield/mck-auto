#!/usr/bin/env python3

import argparse
import importlib.util
import os
import sys
import yaml
import re
import getpass
from datetime import datetime

# import pdb
# pdb.set_trace()
sys.path.append(r'./scripts')
import pmsg
import helper

# CONSTANTS
vcenter_version = "7.0.3"

# Global variables
total_errors = 0
errors = 0

# This script will prepare an on-premise vSphere environment for
# its first deployment of a TKGs workload cluster.


def dprint(msg):
    if verbose is True:
        pmsg.debug(msg)


def confirm_file(filename):
    for fname in os.listdir("."):
        if fname == filename:
            return True
    return False


def add_to_environment(configs):
    count = 0
    for varname in configs:
        if configs[varname] is not None:
            dprint("Putting " + str(varname) + " in the environment...")
            os.environ[varname] = configs[varname]
            os.environ["TF_VAR_"+varname] = configs[varname]
            count += 1
    if count < 1:
        return False
    return True


def read_yaml_config_file(filename):
    # Read configuration file.
    if os.path.exists(filename):
        with open(filename, "r") as cf:
            try:
                configs = yaml.safe_load(cf)
            except yaml.YAMLError as exc:
                pmsg.fail(exc)
                return False, None
    else:
        pmsg.fail("The config file does not exist. Please check the command line and try again.")
        return False, None
    return True, configs


def add_environment_overrides():
    return_code = False
    if os.path.isfile(helper.env_override_file):
        # Add lines to the environment
        rc, configs = read_yaml_config_file(helper.env_override_file)
        if rc:
            if not add_to_environment(configs):
                pmsg.fail("Can't add overrides to the environment.")

        # Delete the environment override file so I don't apply at a later time.
        os.remove(helper.env_override_file)
    return return_code


def run_terraform_init():
    if confirm_file("terraform.tfstate"):
        return False
    return True


def next_step_is_abort(steps, idx):
    if idx >= len(steps) - 1:
        # last line. 
        return False
    if re.match('abort', steps[idx+1], re.IGNORECASE) is not None:
        return True
    return False


def run_terraform(tfolder):
    exit_code = 1
    pmsg.blue("=-=-=-=-=-=-= Running Terraform in " + tfolder + " =-=-=-=-=-=-=-=")
    # cd to that folder
    dir_orig = os.getcwd()
    os.chdir(tfolder)

    # verify that a "main.tf" is here...
    if confirm_file("main.tf"):
        # run terraform init
        result = 0
        if run_terraform_init():
            result = helper.run_a_command("terraform init")
        if result == 0:
            # run terrafor plan
            result = helper.run_a_command("terraform plan -out=myplan.tfplan")
            if result == 0:
                # run terraform apply
                result = helper.run_a_command("terraform apply myplan.tfplan")
                if result == 0:
                    dprint("Terraform of " + tfolder + " completed successfully.")
                    exit_code = 0
                else:
                    pmsg.fail("Terraform apply failed in " + tfolder + ".")
            else:
                pmsg.fail ("Terraform plan -out=myplan.tfplan failed in " + tfolder + ".")
        else:
            pmsg.fail("Terraform init failed in " + tfolder + ".")
    else:
        pmsg.fail("The main.tf file not found in " + tfolder + ".")
    # Leave us back in the original directory
    os.chdir(dir_orig)
    return exit_code

# ########################### Main ################################
# setup args...
help_text = "Run a a pipeline to setup a TKGs "+vcenter_version+" workload cluster on vSphere.\n"
help_text += "Examples:\n"
help_text += "./run_pipeline.py --help\n"

parser = argparse.ArgumentParser(description='Pipeline main script to deploy a TKGs workload cluster.')
parser.add_argument('-c', '--config_file', required=True, help='Name of yaml file which contains config params')
parser.add_argument('-s', '--steps_file', required=True, help='Name of steps file; what scripts will run this time.')
parser.add_argument('-d', '--dry_run', default=False, action='store_true', required=False, help='Just check things... do not make any changes.')
parser.add_argument('-v', '--verbose', default=False, action='store_true', required=False, help='Verbose output.')
parser.add_argument('-n', '--pw_from_env', default=False, action='store_true', required=False, help='PWs from $password.')

args = parser.parse_args()
verbose = args.verbose
dry_run = args.dry_run
password_noprompt = args.pw_from_env

dry_run_flag = ""
if dry_run:
    dry_run_flag = " --dry_run"

verbose_flag = ""
if verbose:
    verbose_flag = " --verbose"

rc, configs = read_yaml_config_file(args.config_file)
if not rc or configs is None:
    pmsg.fail("Can't read the config file: " + args.config_file)
    exit (1)

# First thing to add to the environment is the name of the config file...
if not add_to_environment({"config_file": args.config_file, "steps_file": args.steps_file}):
    pmsg.fail("Can't add the name of the config and steps files to the environment.")

# Read the steps file
if os.path.exists(args.steps_file):
    with open(args.steps_file, "r") as sf:
        steps = sf.read().splitlines()
else:
    pmsg.fail("The steps file does not exist. Please check the command line and try again.")
    exit(1)

###################### Put all the config parameters into the environment ########################
# Setup the environment with all the variables found in the configuration file.
if not add_to_environment(configs):
    pmsg.fail("Can't add config file entries into the environment.")
    exit(1)


# Prompt for password...
if password_noprompt:
    pw = os.environ["password"]
    add_to_environment({"vsphere_password": pw, "tkg_user_password": pw, "avi_vsphere_password": pw, "avi_password": pw})
else:
    prompt_text = "vCenter Admin: " + os.environ["vsphere_username"] + " password: "
    pw1 = getpass.getpass(prompt=prompt_text, stream=None)

    prompt_text = "TKG User: " + os.environ["tkg_user"] + " password: "
    pw2 = getpass.getpass(prompt=prompt_text, stream=None)

    prompt_text = "AVI vSphere " + os.environ["avi_vsphere_username"] + " password: "
    pw3 = getpass.getpass(prompt=prompt_text, stream=None)

    prompt_text = "AVI " + os.environ["avi_username"] + " password: "
    pw4 = getpass.getpass(prompt=prompt_text, stream=None)

    add_to_environment({"vsphere_password": pw1, "tkg_user_password": pw2, "avi_vsphere_password": pw3, "avi_password": pw4})

###################### Execute all the steps in order ########################
abort_exit = False

now = datetime.now()
pmsg.blue("Pipeline starting at: " + str(now))

for idx, step in enumerate(steps):
    step_type = ""
    if abort_exit:
        break

    # Ignore comment/empty lines..match.
    if re.search("^\\s*#|^\\s*$", step) is not None:
        continue

    # What kind of step is this?
    # Is it a script?
    stepname = "./scripts/" + step.strip()
    if os.path.exists(stepname):
        # Must be a script...
        step_type = "script"
        now = datetime.now()
        pmsg.blue(str(now))
        errors = helper.run_a_command(stepname)
        total_errors += errors
        if errors > 0 and next_step_is_abort(steps, idx):
            pmsg.fail("This last script had errors." + steps[idx+1])
            abort_exit = True
        else:
            add_environment_overrides()
        continue


    # Is it a terraform directory?
    try:
        files = os.listdir(step)
        for afile in files:
            if re.search("\\.tf", afile) is not None:
                # I found a .tf file. So must be terraform
                step_type = "terraform"
                now = datetime.now()
                pmsg.blue(str(now))
                errors = run_terraform(step)
                total_errors += errors
                if errors > 0 and next_step_is_abort(steps, idx):
                    pmsg.fail("This last terraform had errors. " + steps[idx+1])
                    abort_exit = True
                break
        if step_type == "terraform":
            continue
    except:
        pass

###################### Done ########################
print ("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
if total_errors > 0:
    pmsg.warning("Number of errors/warnings encountered: " + str(total_errors) + ".")
else:
    pmsg.green("Success! There were no errors or warnings.")

now = datetime.now()
pmsg.blue("Pipeline ending at: " + str(now))