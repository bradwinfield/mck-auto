#!/usr/bin/env python3

# This script will create a config file from the template "create-vsphere-namespace.yaml"
#  and then it will call the wcpctl.py apply <interpolated config file>

import interpolate
import pmsg
import helper
import os

config_file = os.environ["config_file"]
template = "templates/create-vsphere-namespace.yaml"
wcpctl_config = "/tmp/wcpctl_config.yaml"

# Interpolate...
# add vsphere_owner_domain and vsphere_username_nodomain to environment...
vsphere_username = os.environ["vsphere_username"]
parts = vsphere_username.split('@')
os.environ["vsphere_username_nodomain"] = parts[0]
os.environ["vsphere_owner_domain"] = parts[1]
interpolate.interpolate_from_environment_to_template(template, wcpctl_config)

# Run wcpctl.py
os.environ["WCP_PASSWORD"] = os.environ["vsphere_password"]
rc = helper.run_a_command("./scripts/wcpctl.py apply " + wcpctl_config)
if rc != 0:
    pmsg.fail("Failed to create the vSphere namespace.")

# Clean up first...
os.remove(wcpctl_config)
exit(rc)
