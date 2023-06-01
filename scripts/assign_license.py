#!/usr/bin/env python3

# This step will assign the Tanzu Standard License to the Supervisor Cluster in vCenter.

import os
import pmsg
import vsphere_mob
import pdb

# Get server and credentials from the environment...
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
cluster_name = os.environ["cluster_name"]

mob = vsphere_mob.vsphere_mob(False)
c = mob.login(vsphere_server, vsphere_username, vsphere_password, True)
content = c.content
if content is None:
    pmsg.fail("Could not login to the MOB SOAP API. Check your user credentials in the config.yaml and try again. Exiting.")
    exit (2)

license_manager = content.licenseManager
pdb.set_trace()

# license_manager.licenses is an array of vim.LicenseManager.LicenseInfo
# look for .name = 'Tanzu Standard activation for vSphere' (or similar)
# in license_manager.licenses[].name
# find key in license_manager.licenses[].licenseKey
#


# Get the supervisor cluster object.
cluster_url = f"{vsphere_server}/api/vcenter/clusters/{cluster_name}"
supervisor_cluster = session.get(cluster_url).json()

# Get the license key.
license_key = "your_license_key"

# Assign the license to the supervisor cluster.
license_assignment_url = f"{vcenter_server}/api/vcenter/licenseAssignments"
data = {
    "licenseKey": license_key,
    "entity": supervisor_cluster["id"],
}
response = session.post(license_assignment_url, data=data)

# Check the response status code.
if response.status_code == 200:
    print("License assigned successfully.")
else:
    print("Error assigning license.")
