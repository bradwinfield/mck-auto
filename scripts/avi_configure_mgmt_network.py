#!/usr/bin/env python3

import requests
import json
import os
import urllib3
import helper_avi
import pmsg
import pdb
import re

urllib3.disable_warnings()

# Get local variables from environment to make it cleaner looking code.
avi_vm_ip1 = os.environ["avi_vm_ip1"]
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
avi_network = os.environ["avi_network"]
avi_network_ip = os.environ["avi_network_ip"]
supervisor_network_static_ip_pool = os.environ["supervisor_network_static_ip_pool"]
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
vsphere_datacenter = os.environ["vsphere_datacenter"]

avi_vm_ip = avi_vm_ip1
if "avi_vm_ip_override" in os.environ.keys():
    avi_vm_ip = os.environ["avi_vm_ip_override"]
api_endpoint = "https://" + avi_vm_ip

def get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token):
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password)
    response = requests.get(api_endpoint + path, verify=False, headers=headers, cookies=dict(sessionid=login_response.cookies['sessionid']))

    network_details = json.loads(response.text)

    if response.status_code == 200:
        return response, network_details
    else:
        pmsg.fail("Error retrieving network config: " + str(response.status_code) + response.text)
    return response, None

def put_avi_object(api_endpoint, login_response, obj_details, avi_vm_ip, avi_username, avi_password, token):

    # send it back
    uuid = network["uuid"]
    path = "/api/network/" + uuid

    # Must set the header and the cookie for a PUT call...
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password)
    cookies = helper_avi.get_next_cookie_jar(login_response, None, avi_vm_ip, token)
    pdb.set_trace()
    response = requests.put(api_endpoint + path, verify=False, json=obj_details, headers=headers, cookies=cookies)
    if response.status_code < 300:
        return True
    return False


# ################### LOGIN ###############################################
# Login and get session ID...
logged_in = False
exit_code = 1
login_response = helper_avi.login(api_endpoint, False, avi_username, avi_password)
if login_response.status_code >= 300:
    pmsg.fail("Can't login to AVI.")
    exit(exit_code)
logged_in = True
token = helper_avi.get_token(login_response, "")

# ##################### GET AVI Object #############################################
# If modifying an AVI object, get the current configuration of whatever you are going to modify...
path = "/api/network"
response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if obj_details is not None:
    token = helper_avi.get_token(response, token)

    # walk through all the network objects
    found_network = False
    for network in obj_details["results"]:
        if network["name"] == avi_network:
            found_network = True
            # This the network to modify
            update_network = network
            pmsg.green("AVI network found OK.")
            break

    if found_network:
        # Now update the update_network and PUT it back
        avi_network_ip_parts = re.split('/', avi_network_ip)
        network_number = avi_network_ip_parts[0]
        mask = int(avi_network_ip_parts[1])
        begin_end = re.split('\-', supervisor_network_static_ip_pool)

        prefix = {
            "ip_addr": {"addr": network_number, "type": "V4"}, "mask": mask
        }

        static_ip_range = {
            "range": {
                "begin":
                    {"addr": begin_end[0], "type": "V4"},
                "end":
                    {"addr": begin_end[1], "type": "V4"}
            },
            "type": "STATIC_IPS_FOR_VIP_AND_SE"
        }

        configured_subnet = [{"prefix": prefix, "static_ip_ranges": [static_ip_range]}]
        update_network["configured_subnets"] = configured_subnet

        if put_avi_object(api_endpoint, response, update_network, avi_vm_ip, avi_username, avi_password, token):
            pmsg.green("AVI network updated OK.")
            exit_code = 0
        else:
            pmsg.fail("Can't update the network in AVI: " + str(response.status_code) + " " + response.text)
    else:
        pmsg.fail("Can't find network: " + avi_network + " in AVI.")
else:
    pmsg.fail("Can't get network information from AVI.")

if logged_in:
    helper_avi.logout(api_endpoint, login_response, avi_vm_ip, avi_username, avi_password, token)

exit(exit_code)
