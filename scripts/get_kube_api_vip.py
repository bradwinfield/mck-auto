#!/usr/bin/env python3
import requests
import json
import os
import urllib3
import helper
urllib3.disable_warnings()

# Set up the API endpoint and authentication details
server = os.environ["avi_controller_ip"]
api_endpoint = "https://" + server
avi_user = os.environ["avi_username"]
avi_password = os.environ["avi_password"]

# Set up the HTTP headers and authentication token
headers = {
    "Content-Type": "application/json",
}
#    "X-Avi-Version": "18.2.7",
auth = (avi_user, avi_password)

# Login and get session ID...
login = requests.post(api_endpoint + "/login", verify=False, data={'username': 'admin', 'password': avi_password})

# Send a GET request to the API endpoint to retrieve the list of virtual services
response = requests.get(api_endpoint + "/api/vsvip", verify=False, cookies=dict(sessionid= login.cookies['sessionid']))

# Parse the response and retrieve the VIPs
if response.status_code == 200:
    vs_list = json.loads(response.text)
    for vs in vs_list["results"]:
        if "--kube-system-kube-apiserver-lb-svc" in vs["name"]:
            for vip in vs["vip"]:
                print(vip["ip_address"]["addr"])
                helper.add_env_override(True, "supervisor_cluster", vip["ip_address"]["addr"])
else:
    print("Error retrieving virtual services: ", response.text)
