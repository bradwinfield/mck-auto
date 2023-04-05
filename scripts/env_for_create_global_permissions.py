#!/usr/bin/env python3

# Class and Methods for interacting with the MOB3 SOAP interface.

import requests
import re
import os
import pdb
import helper
import pmsg
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

vsphere_server = os.environ["vsphere_server"]
username = os.environ["vsphere_username"]
password = os.environ["vsphere_password"]
tkg_role = os.environ["tkg_role"]

# Create a session and set the authentication headers
session = requests.session()
session.auth = (username, password)

# Make a GET request to retrieve information from the vSphere MOB
full_url = "https://" + vsphere_server + "/invsvc/mob3/?moid=authorizationService&method=AuthorizationService.GetRoles"
response = session.get(full_url, verify=False)

if response.status_code == 200:
    nonce = re.split('"',re.split('vmware-session-nonce. type=.hidden. value=.', response.content.decode())[1])[0]
    post_data = "vmware-session-nonce=" + nonce

    # Add a global permission...
    full_url_post = full_url + "&" + post_data 
    response2 = session.post(full_url_post, verify=False)

    if response2.status_code == 200:
        # Parse the HTML body and pull out the TKG role name and find the ID...
        sections = re.split('<tr><th>Name</th><th>Type</th><th>Value</th>',response2.text)
        for section in sections:
            if 'name</td><td class="c1">string</td><td>' + tkg_role + '</td>' in section:
                pdb.set_trace()
                # Parse out the ID for this role...
                parts = re.search('id</td><td class="c1">long</td><td>(\d+)</td>', section)
                helper.add_env_override(True, "tkg_role_id", parts[1])
    else:
        pmsg.fail("Can't find role list in vCenter.")
        exit(1)
exit(0)
