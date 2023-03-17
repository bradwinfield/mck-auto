#!/usr/bin/env python3

import argparse
import importlib.util
import os
import sys
import yaml

# import pdb
# pdb.set_trace()
sys.path.append(r'./scripts')
import pmsg
import helper

# CONSTANTS
vcenter_version = "7.0.3"

# Global variables
total_errors = 0

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


def need_terraform_init():
    if confirm_file("terraform.tfstate"):
        return False
    return True


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
        if need_terraform_init():
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
# Setup the environment with all the variables found in the configuration file.
for varname in configs:
    if configs[varname] is not None:
        dprint("Putting " + str(varname) + " in the environment...")
        os.environ[varname] = configs[varname]
        os.environ["TF_VAR_"+varname] = configs[varname]

###################### Next Step ########################
# Login to the k8s cluster...
total_errors += helper.run_a_command("./scripts/k8s_cluster_login.py")

###################### Next Step ########################
# Check/Create Users (TKG and AVI). Terraform does not appear to do this.
total_errors += helper.run_a_command("./scripts/check_users.py -c " + args.config_file)

###################### Next Step ########################
# Check/Change Storage Class to be the default...
total_errors += helper.run_a_command("./scripts/check_sc.py")

###################### Next Step ########################
# Run terraform for folders
total_errors += run_terraform("terraform")

###################### Done ########################
print ("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
if total_errors > 0:
    pmsg.warning("Number of errors/warnings encountered: " + str(total_errors) + ".")
else:
    pmsg.green("Success! There were no errors or warnings.")
pmsg.blue ("Done.")