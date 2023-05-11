#!/usr/bin/env python3

# Checks for storage policy; creates it if missing.

import vcenter_api
import vsphere_mob
import pmsg
import os
import helper
import pdb

def create_resource_pool(vsphere_server, token, resource_pool, vsphere_cluster_id, parent_resource_pool_id):
    found_rg = False
    json_data = {"name": resource_pool, "parent": parent_resource_pool_id}
    id = vcenter_api.api_post_returns_content(vsphere_server, "/api/vcenter/resource-pool", token, json_data, 201)
    if id is not None:
        pmsg.green ("Resource Pool: " + resource_pool + " created.")
        found_rg = True
        helper.add_env_override(True, "avi_resource_pool_id", id.decode().strip('"'))
    else:
        pmsg.fail ("I can't create the Resource Group: " + resource_pool + ". You may want to create it manually. Please check Resource groups in vCenter and try again.")
    return found_rg

def use_mob():
    mob = vsphere_mob.vsphere_mob(False)
    c = mob.login(vsphere_server, vsphere_username, vsphere_password, True)
    content = c.content
    if content is None:
        pmsg.fail("Could not login to the MOB SOAP API. Check your user credentials in the config.yaml and try again. Exiting.")
        exit (2)

    storage_policy_manager = content.storageResourceManager
    pdb.set_trace()


################################ Main #############################

vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
storage_class = os.environ["storage_class"]

# use_mob()

token = vcenter_api.vcenter_login(vsphere_server, vsphere_username, vsphere_password)
if len(token) < 1:
    pmsg.fail("No token obtained from login api call to vSphere. Check your user credentials in the config.yaml and try again. Exiting.")
    exit (9)

exit_code = 1

response = vcenter_api.api_get(vsphere_server, "/api/vcenter/storage/policies", token)
if response is not None:
    for policy in response:
        pmsg.normal("Name: = " + policy["name"])
        if policy["name"] == storage_class:
            pmsg.green("Storage Policy is OK.")
            pdb.set_trace()
            exit(0)

pmsg.normal("Creating Storage Policy: " + storage_class + "...")

exit(exit_code)
