#!/usr/bin/env python3

import os
import json
import requests
import pdb
import pmsg
import urllib3
urllib3.disable_warnings()

# Queries the AVI controller to see if HA is enabled.
# If not, then enables HA.

def set_ha_data(current_config, avi_vm_ip1, avi_vm_ip2, avi_vm_ip3, avi_floating_ip):
    # current_config["uuid"]
    # current_config["name"]
    current_config["virtual_ip"] = {"type": "V4", "addr": avi_floating_ip}
    current_config["nodes"].append({"name": avi_vm_ip2, "ip": {"type": "V4", "addr": avi_vm_ip2}})
    current_config["nodes"].append({"name": avi_vm_ip3, "ip": {"type": "V4", "addr": avi_vm_ip3}})
    return True


def get_ha_data(current_config, avi_vm_ip1, avi_vm_ip2, avi_vm_ip3, avi_floating_ip):
    json_put_data = {
        "uuid": current_config["uuid"],
        "name": current_config["name"],
        "virtual_ip": {"type": "V4", "addr": avi_floating_ip},
        "nodes": [
            {
                "ip": {
                    "type": "V4",
                    "addr": avi_vm_ip1
                },
                "vm_hostname": current_config["nodes"][0]["vm_hostname"],
                "vm_uuid": current_config["nodes"][0]["vm_uuid"],
                "name": current_config["nodes"][0]["name"]
            },
            {
                "ip": {"type": "V4", "addr": avi_vm_ip2},
                "name": avi_vm_ip2
            },
            {
                "ip": {"type": "V4", "addr": avi_vm_ip3},
                "name": avi_vm_ip3
            }
        ]
    }

    return json_put_data

avi_floating_ip = os.environ["avi_floating_ip"]
avi_vm_ip1 = os.environ["avi_vm_ip1"]
avi_vm_ip2 = os.environ["avi_vm_ip2"]
avi_vm_ip3 = os.environ["avi_vm_ip3"]

server = avi_vm_ip1
api_endpoint = "https://" + server
avi_user = os.environ["avi_username"]
avi_password = os.environ["avi_password"]

# Login and get session ID...
login = requests.post(api_endpoint + "/login", verify=False, data={'username': 'admin', 'password': avi_password})
if login.status_code != 200:
    pmsg.fail("Can't login to ", api_endpoint)
    exit(1)

# What is the current configuration?
path = "/api/cluster"
# response = requests.get(api_endpoint + path, verify=False, cookies=dict(sessionid= login.cookies['sessionid']))
response = requests.get(api_endpoint + path, verify=False, cookies=login.cookies)
if response.status_code != 200:
    pmsg.fail("Can't get cluster config from: " + api_endpoint)
    exit(1)

pdb.set_trace()
# Parse the response and retrieve the current configuration
current_config = json.loads(response.text)
if len(current_config["nodes"]) < 2:
    # Turn on HA mode
    data = get_ha_data(current_config, avi_vm_ip1, avi_vm_ip2, avi_vm_ip3, avi_floating_ip)
    headers={
        'X-CSRFToken': login.cookies['csrftoken'],
        'Referer': api_endpoint,
        "Content-Type": "application/json",
        "Accept-Encoding": "application/json",
        "X-Avi-Version": "22.1.3"
        }

    # Send it back via http PUT...
    response = requests.put(api_endpoint + path, verify=False, data=data, headers=headers, cookies=login.cookies)
    if response.status_code != 200:
        pmsg.fail("Can't turn on HA mode in AVI. HTTP Error: " + str(response.status_code))
        exit(1)

exit(0)
