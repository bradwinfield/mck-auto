#!/usr/bin/env python3

import requests
import json
import os
import urllib3
import helper_avi
import pmsg

urllib3.disable_warnings()

# Get local variables from environment to make it cleaner looking code.
avi_vm_ip1 = os.environ["avi_vm_ip1"]
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
avi_data_network_ref = os.environ["avi_data_network_ref"]
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
vsphere_datacenter = os.environ["vsphere_datacenter"]

avi_vm_ip = avi_vm_ip1
if "avi_vm_ip_override" in os.environ.keys():
    avi_vm_ip = os.environ["avi_vm_ip_override"]
api_endpoint = "https://" + avi_vm_ip

def get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token):
    # Send a GET request to the API endpoint to retrieve the Default-Cloud details...
    # return json object of config
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password)
    response = requests.get(api_endpoint + path, verify=False, headers=headers, cookies=dict(sessionid=login_response.cookies['sessionid']))

    ipam_details = json.loads(response.text)

    if response.status_code == 200:
        return response, ipam_details
    else:
        pmsg.fail("Error retrieving IPAM configs: " + str(response.status_code) + response.text)
    return response, None

def post_avi_object(api_endpoint, login_response, obj_details, avi_vm_ip, avi_username, avi_password, token):
    # send it back
    path = "/api/ipamdnsproviderprofile"

    # Must set the header and the cookie for a PUT call...
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password)
    cookies = helper_avi.get_next_cookie_jar(login_response, None, avi_vm_ip, token)
    response = requests.post(api_endpoint + path, verify=False, json=obj_details, headers=headers, cookies=cookies)
    if response.status_code < 300:
        pmsg.green("AVI object updated.")
        return True
    else:
        pmsg.fail("Can't update AVI object: " + str(response.status_code) + ": " + response.text)
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
path = "/api/ipamdnsproviderprofile"
response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if obj_details is not None:
    token = helper_avi.get_token(response, token)

    #  Sample of what came back
    # {"count": 0, "results": []}
    if obj_details["count"] == 0:
        # Here is what I need to send back (POST)
        ipam_profile = {
            # "_last_modified": "1682517665712989",
            "allocate_ip_in_vrf": False,
            "internal_profile": {
                "ttl": 30,
                "usable_networks": [
                    {
                        "nw_ref": avi_data_network_ref
                    }
                ]
            },
            "name": "vip-data-network",
            "tenant_ref": "https://" + avi_vm_ip + "/api/tenant/admin",
            "type": "IPAMDNS_TYPE_INTERNAL",
            # "url": "https://10.220.30.131/api/ipamdnsproviderprofile/ipamdnsproviderprofile-f1dd823c-fdff-4510-88cb-88c11d44099a",
            # "uuid": "ipamdnsproviderprofile-f1dd823c-fdff-4510-88cb-88c11d44099a"
        }

# ##################### PUT AVI Object #############################################
        if post_avi_object(api_endpoint, response, ipam_profile, avi_vm_ip, avi_username, avi_password, token):
            pmsg.green("AVI IPAM profile for the data/vip network OK.")
            exit_code = 0
        else:
            pmsg.fail("Can't create IPAM profile for the data/vip network in AVI: " + str(response.status_code) + " " + response.text)
    else:
        pmsg.fail("Expected no IPAM profiles.")
else:
    pmsg.fail("Can't retrieve AVI data from path: " + path + ".")

if logged_in:
    helper_avi.logout(api_endpoint, login_response, avi_vm_ip, avi_username, avi_password, token)

exit(exit_code)

