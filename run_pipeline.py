#!/usr/bin/env python3

import argparse
import importlib.util
import os
import sys
import yaml
import re
import getpass
import shutil
import stat
from datetime import datetime

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

def confirm_file(filename):
    for fname in os.listdir("."):
        if fname == filename:
            return True
    return False

def exit_with_messages(total_errors):
    pmsg.normal ("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    if total_errors > 0:
        pmsg.warning("Number of errors/warnings encountered: " + str(total_errors) + ".")
    else:
        pmsg.green("Success! There were no errors or warnings.")

    now = datetime.now()
    pmsg.blue("Pipeline ending at: " + str(now))
    exit(total_errors)

def add_to_environment(configs):
    count = 0
    for varname in configs:
        if configs[varname] is not None:
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


def add_environment_overrides(file):
    return_code = False
    if os.path.isfile(file):
        # Add lines to the environment
        rc, configs = read_yaml_config_file(file)
        if rc:
            if not add_to_environment(configs):
                pmsg.fail("Can't add overrides to the environment.")

        # Delete the environment override file so I don't apply at a later time.
        if file == helper.env_override_file:
            os.remove(file)
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

def site_terraform(tfolder, vsphere_server, site_name):
    # parse vsphere_server to get the site name
    site_dir = "site_terraform/" + site_name
    terraform_dir = site_dir + "/" + tfolder
    # if site_terraform does not exist, create it
    if not os.path.isdir("site_terraform"):
        os.mkdir("site_terraform")
        os.chmod("site_terraform", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    # if the site_dir does not exist, create it
    if not os.path.isdir(site_dir):
        os.mkdir(site_dir)
        os.chmod(site_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    if not os.path.isdir(terraform_dir):
        # and copy in the tfolder (template) tf files...
        shutil.copytree(tfolder, terraform_dir)
        os.chmod(terraform_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    # return the site_dir
    return terraform_dir

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
help_text += "./run_pipeline.py -c config.yaml -s steps.conf -p access.yaml\n"

parser = argparse.ArgumentParser(description='Pipeline main script to deploy a TKGs workload cluster.')
parser.add_argument('-c', '--config_file', required=True, help='Name of yaml file which contains config params')
parser.add_argument('-s', '--steps_file', required=True, help='Name of steps file; what scripts will run this time.')
parser.add_argument('-p', '--password_file', required=False, help='Name of additional configs file (secrets).')

args = parser.parse_args()
password_file = args.password_file

rc, configs = read_yaml_config_file(args.config_file)
if not rc or configs is None:
    pmsg.fail("Can't read the config file: " + args.config_file)
    exit (1)

# Just in case a prior environment override file exists... delete it.
if os.path.isfile(helper.env_override_file):
    os.remove(helper.env_override_file)

# Add to the environment the name of the config file...
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

#site_name = re.split('\.', configs["vsphere_server"])[0]
site_name = configs["vsphere_server"][0:4]
if not add_to_environment({"site_name": site_name}):
    pmsg.fail("Can't add the site name to the environment.")

if "USER" in os.environ.keys():
    user = os.environ["USER"]
    if re.search(' ', user) is not None:
        add_to_environment("USER", user.replace(' ', ''))
else:
    add_to_environment("USER", "no_user")

# Some automation steps can only use one NTP or DNS server, so create singleton variables...
if "dns_servers" in configs.keys():
    parts = re.split(' |,|;', configs["dns_servers"].replace(" ", ""))
    add_to_environment({"dns_server": parts[0]})
if "ntp_servers" in configs.keys():
    parts = re.split(' |,|;', configs["ntp_servers"].replace(" ", ""))
    add_to_environment({"ntp_server": parts[0]})

# Get passwords from file or prompt for password...
if password_file is not None:
    add_environment_overrides(password_file)
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
    if re.search("^\\s*#|^\\s*$|^abort", step, re.IGNORECASE) is not None:
        if re.search("^abort", step, re.IGNORECASE) is None:
            pmsg.normal(step)
        continue

    # If step is an "exit", then exit.
    if re.match("exit", step, re.IGNORECASE):
        pmsg.normal(step)
        pmsg.normal("Step processing stopping now due to 'exit' statement in step file.")
        exit_with_messages(total_errors)

    ran_step = False
    # What kind of step is this?
    # Is it a script?
    step_parts = step.split()
    stepname = "./scripts/" + step_parts[0]
    if os.path.exists(stepname):
        # Must be a script...
        step_type = "script"
        now = datetime.now()
        pmsg.blue(str(now))
        arguments = ""
        if len(step_parts) > 1:
            arguments = " ".join(step_parts[1:len(step_parts)])
        errors = helper.run_a_command(stepname + " " + arguments)
        ran_step = True
        total_errors += errors
        if errors > 0 and next_step_is_abort(steps, idx):
            pmsg.fail("This last script had errors." + steps[idx+1])
            abort_exit = True
        else:
            add_environment_overrides(helper.env_override_file)
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
                errors = run_terraform(site_terraform(step, configs["vsphere_server"], site_name))
                ran_step = True
                total_errors += errors
                if errors > 0 and next_step_is_abort(steps, idx):
                    pmsg.fail("This last terraform had errors. " + steps[idx+1])
                    abort_exit = True
                break
        if step_type == "terraform":
            continue
    except:
        pass

    if not ran_step:
        pmsg.warning("Line ignored in step file: " + step + " Check your step file.")

###################### Done ########################
exit_with_messages(total_errors)
