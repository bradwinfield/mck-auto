#!/usr/bin/env python3
import requests
import json
import os
import urllib3
import helper
import time
import pdb

urllib3.disable_warnings()


# ################################## Main ################################
# Set up the API endpoint and authentication details
# If we have a DNS entry pre-created for AVI at this DC, then use this...
#server = os.environ["avi_controller_ip"]
# If not, use the IP address...
server = os.environ["avi_vm_ip1"]
api_endpoint = "https://" + server
avi_user = os.environ["avi_username"]
avi_password = os.environ["avi_password"]

# Set up the HTTP headers and authentication token
headers = {
    "Content-Type": "application/json",
}
#    "X-Avi-Version": "18.2.7",
pdb.set_trace()
auth = (avi_user, avi_password)

# Login and get session ID...
login = requests.post(api_endpoint + "/login", verify=False, data={'username': 'admin', 'password': avi_password})

exit(0)
