#!/usr/bin/env python3

# Checks for and creates the AVI resource group.

import vcenter_api
import pmsg
import argparse
import os
import helper

def dprint(msg):
    if verbose:
        pmsg.debug(msg)

def check_resource_pool(server, token, resource_pool, cluster_id):
    found_rg = False
    # curl -X GET 'https://vc01.h2o-75-9210.h2o.vmware.com/api/vcenter/resource-pool?names=AVI&clusters=domain-c8'
    path = "/api/vcenter/resource-pool?names=" + resource_pool + "&clusters=" + cluster_id
    json_obj = vcenter_api.api_get_(server, path, token)
    if json_obj is not None:
        found_rg = True
    if not found_rg:
        dprint ("Creating resource group: " + resource_pool)
        json_dta = {"name": resource_pool, "parent": ""}
        rc = vcenter_api.api_post(server, "/api/vcenter/resource-pool", token, json_data, 201)
        if rc:
            pmsg.green ("Resource Group: " + resource_pool + " created.")
            found_rg = True
        else:
            pmsg.fail ("I can't create the Resource Group: " + resource_pool + ". You may want to create it manually. Please check Resource groups in vCenter and try again.")
    return found_rg


################################ Main #############################
# setup args...
help_text = "Create/Check vCenter Resource Group for AVI install."

server = os.environ["vsphere_server"]
username = os.environ["vsphere_username"]
password = os.environ["vsphere_password"]
avi_resource_pool = os.environ["avi_resource_pool"]
cluster_id = os.environ["cluster_id"]

token = vcenter_api.vcenter_login(server, username, password)
if len(token) < 1:
    pmsg.fail("No token obtained from login api call to vSphere. Check your user credentials in the config.yaml and try again. Exiting.")
    exit (9)
dprint ("Session Token for REST API: " + token)

exit_code = 0

if check_resource_pool(server, token, avi_resource_pool, cluster_id):
    pmsg.green("Resource Pool: " + avi_resource_pool + " OK.")
else:
    pmsg.fail("Resource Pool: " + avi_resource_pool + " not OK.")
    exit_code += 1

exit(exit_code)
