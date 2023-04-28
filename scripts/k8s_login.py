#!/usr/bin/env python3

# Logs into the TKGs Cluster with the os.environ["login_user"]/os.environ["login_password"] user.
# This is called by
# - k8s_supervisor_login_admin.py
# - k8s_supervisor_login.py

import os
import helper
import re
import subprocess
import pmsg
import time
# import pdb

# Did the VIP get set?
if "supervisor_cluster_vip" not in os.environ.keys():
    pmsg.fail("The VIP for the supervisor cluster VIP was not provided/found.")
    exit(1)

supervisor_cluster = os.environ["supervisor_cluster"]
supervisor_cluster_vip = os.environ["supervisor_cluster_vip"]
vsphere_namespace = os.environ["vsphere_namespace"]
vsphere_username = os.environ["login_user"]
os.environ["KUBECTL_VSPHERE_PASSWORD"] = os.environ["login_password"]
vsphere_namespace = os.environ["vsphere_namespace"]


def try_to_login(command):
    if helper.run_a_command(command) == 0:
        # Connect to the context
        command = "kubectl config use-context " + supervisor_cluster_vip

        if helper.run_a_command(command) == 0:
            # Verify that I'm logged in...
            process = subprocess.Popen(["kubectl", "config", "get-contexts"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = process.communicate()
            contexts = output.splitlines()
            for context in contexts:
                if re.search("\\*\\s+"+supervisor_cluster_vip+"\\s", context.decode('utf-8')) is not None:
                    pmsg.green("k8s supervisor cluster login as " + vsphere_username + " OK.")
                    return True
    return False


# ##################################### Main ###############################
login_command = "kubectl vsphere login --server " + supervisor_cluster_vip + " --vsphere-username " + vsphere_username + " --insecure-skip-tls-verify"

logged_in = False
exit_code = 1
for i in range(1, 30):
    # Try to login until either I'm successful or I try too many times.
    logged_in = try_to_login(login_command)
    if logged_in:
        exit_code = 0
        pmsg.green("Log in OK.")
        break
    pmsg.notice("Will try again in a minute...")
    time.sleep(50)

exit(exit_code)
