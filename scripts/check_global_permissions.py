#!/usr/bin/env python3

# Class and Methods for interacting with the MOB3 SOAP interface.

import requests
import re
import os
# import urllib.parse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

vsphere_server = os.environ["vsphere_server"]
username = os.environ["vsphere_username"]
password = os.environ["vsphere_password"]
tkg_user = os.environ["tkg_user"]
tkg_role = os.environ["tkg_role"]
tkg_role_id = os.environ["tkg_role_id"]

# Create a session and set the authentication headers
session = requests.session()
session.auth = (username, password)
# sessionjar = requests.cookies.RequestsCookieJar()

# Make a GET request to retrieve information from the vSphere MOB
full_url = "https://" + vsphere_server + "/invsvc/mob3/?moid=authorizationService&method=AuthorizationService.AddGlobalAccessControlList"
response = session.get(full_url, verify=False)
# response = session.get(full_url, cookies=sessionjar, verify=False)

if response.status_code == 200:
    nonce = re.split('"',re.split('vmware-session-nonce. type=.hidden. value=.', response.content.decode())[1])[0]
    permissions_body = "<permissions><principal><name>" + tkg_user + "</name><group>false</group></principal><roles>" + tkg_role_id + "</roles><propagate>true</propagate></permissions>"
    post_data = "vmware-session-nonce=" + nonce + "&permissions=" + permissions_body

    # Add a global permission...
    full_url_post = full_url + "&" + post_data 
    response2 = session.post(full_url_post, verify=False)
    # response2 = session.post(full_url_post, cookies=sessionjar, verify=False)

    if response2.status_code != 200:
        pmsg.fail("Can't add user/role: " + tkg_user + "/" + tkg_role_id + ".")
        exit(1)
exit(0)
