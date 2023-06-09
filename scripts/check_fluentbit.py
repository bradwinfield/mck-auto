#!/usr/bin/env python3

# Checks to see if fluent-bit is installed and running.
# If not, installs it.
# Assumes the package is in the cluster already.
# Assumes that the commands 'tanzu' and 'kubectl' are available.
# Assumes we are logged-in to the cluster and the context is already set.

import helper
import pmsg
import re
import os
import interpolate

package_namespace = os.environ["installed_packages_namespace"]
site_name = os.environ["site_name"]
values_file = "templates/fluent-bit-default-values.yaml"
user = os.environ["USER"]
completed_values_file = "/tmp/" + user + "_" + site_name + "-fluent-bit-default-values.yaml"
interpolate.interpolate_from_environment_to_template(values_file, completed_values_file)

# Is fluent-bit already running?
if False:
    pmsg.green("The fluent-bit is OK.")

else:
    # Check for fluent-bit as an available package: tanzu package available list -A | grep fluent-bit
    found_cm = False
    lines = helper.run_a_command_get_stdout(["tanzu", "package", "available", "list", "fluent-bit.tanzu.vmware.com"])
    if lines is not None:
        for line in lines:
            if re.match('\\s*fluent-bit.tanzu.vmware.com', line) is not None:
                fb_version = re.split('\\s+', line)[1]
                found_cm = True

    if found_cm:
        # Interpolate values file...
        helper.run_a_command_list(["tanzu", "package", "install", "fluent-bit", "--package-name", "fluent-bit.tanzu.vmware.com", "--values-file", completed_values_file, "--namespace", package_namespace, "--version", fb_version, "--create-namespace"])

        # Run the command to check for reconciliation complete...
        print("Checking for reconcile...")
        reconciled = helper.check_for_result_for_a_time(["tanzu", "package", "installed", "list", "-A"], 'fluent-bit.*Reconcile succeeded', 10, 36)
        # clean-up completed values file...
        os.remove(completed_values_file)
        if reconciled:
            pmsg.green("The fluent-bit is OK.")
        else:
            pmsg.fail("Failed to install fluent-bit. Check the logs.")
            exit(1)
    else:
        pmsg.fail("The fluent-bit package can't be found.")
        exit(1)
exit(0)
