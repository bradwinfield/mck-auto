#!/usr/bin/env python3

import os
import json
import requests
import pmsg
import pdb
import urllib3
urllib3.disable_warnings()

# Configures the Default-Cloud if not already configured.
# Needs avi_content_library_id: run step "env_for_library_id.py" before this step.

avi_floating_ip = os.environ["avi_floating_ip"]
avi_vsphere_username = os.environ["avi_vsphere_username"]
avi_vsphere_password = os.environ["avi_vsphere_password"]
vsphere_datacenter = os.environ["vsphere_datacenter"]
vsphere_server = os.environ["vsphere_server"]
avi_content_library = os.environ["avi_content_library"]
avi_content_library_id = os.environ["avi_content_library_id"]
server = avi_floating_ip
api_endpoint = "https://" + server
avi_user = os.environ["avi_username"]
avi_password = os.environ["avi_password"]

# Login and get session ID...
login = requests.post(api_endpoint + "/login", verify=False, data={'username': 'admin', 'password': avi_password})
if login.status_code > 299:
    pmsg.fail("Can't login to " + api_endpoint + ". HTTP Status Code: " + str(login.status_code) + ". " + login.text)
    exit(1)

# What is the current configuration of all clouds?
path = "/api/cloud"
response = requests.get(api_endpoint + path, verify=False, cookies=login.cookies)
if response.status_code > 299:
    pmsg.fail("Can't get cloud config from: " + api_endpoint + path + ". HTTP Status Code: " + str(response.status_code) + ". " + response.text)
    exit(1)

# If the current configuration includes all three of the AVI controllers,
# then we are done.
current_config = json.loads(response.text)
reconfigure = False

if current_config["count"] != 1:
    pmsg.warning("AVI seems to have already been configured with multiple 'Clouds'. There should only be 'Default-Cloud'. Recommend manual configuration.")
    exit(1)

if current_config["results"][0]["vtype"] == "CLOUD_NONE":
    # Set the cloud type to vCenter...
    reconfigure = True

current_config["results"][0]["vtype"] = "CLOUD_VCENTER"
current_config["results"][0]["vcenter_configuration"] = {
    "datacenter": vsphere_datacenter,
    "password": avi_vsphere_password,
    "privilege": "WRITE_ACCESS",
    "username": avi_vsphere_username,
    "vcenter_url": vsphere_server,
    "use_content_lib": "false",
#    "content_lib": {
#      "name": avi_content_library,
#      "id": avi_content_library_id
#    }
}

# POST it back to the server...
headers = {
    "Referer": api_endpoint + "/api/cloud",
    "Content-Type": "application/json",
    "Accept-Encoding": "application/json",
    "X-CSRFToken": login.cookies["csrftoken"],
    "X-Avi-Version": "22.1.3"
}

uuid = current_config["results"][0]["uuid"]
put_url = api_endpoint + path + "/" + uuid + "?include_name"
# Send it back via http POST...
data = str(current_config["results"][0]).replace("'", '"').replace(" False,", " false,").replace(" True,", " true,")
pdb.set_trace()
response = requests.put(put_url, verify=False, data=data, headers=headers, cookies=login.cookies)
if response.status_code > 299:
    pmsg.fail("Can't configure AVI. HTTP Error: " + str(response.status_code) + ". " + response.text)
    exit(1)

pmsg.green("AVI Config OK.")

exit(0)
