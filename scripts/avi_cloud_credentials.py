#!/usr/bin/env python3

import requests
import json
import os
import urllib3
import helper_avi
import pmsg

urllib3.disable_warnings()

avi_vm_ip = os.environ["avi_vm_ip1"]
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
vsphere_datacenter = os.environ["vsphere_datacenter"]

server = os.environ["avi_vm_ip"]
api_endpoint = "https://" + server

def get_cloud_details(api_endpoint, login_response, avi_username, avi_password, token):
    # Send a GET request to the API endpoint to retrieve the Default-Cloud details...
    # return json object of config
    path = "/api/cloud"
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password)
    response = requests.get(api_endpoint + path, verify=False, headers=headers, cookies=dict(sessionid=login_response.cookies['sessionid']))

    cloud_details = json.loads(response.text)

    if response.status_code == 200:
        return response, cloud_details
    else:
        pmsg.fail("Error retrieving cloud config: " + str(response.status_code) + response.text)
    return response, None

def set_cloud_details(api_endpoint, login_response, cloud_details, avi_vm_ip, avi_username, avi_password, token):
    # Update cloud_details json to set the Default-Cloud vCenter credentials...
    default_cloud_details = cloud_details["results"][0]
    default_cloud_details["vcenter_configuration"] = {
        "datacenter": vsphere_datacenter,
        "password": vsphere_password,
        "privilege": "WRITE_ACCESS",
        "username": vsphere_username,
        "use_content_lib": False,
        "vcenter_url": vsphere_server
    }
    default_cloud_details["vtype"] = "CLOUD_VCENTER"
    uuid = default_cloud_details["uuid"]

    # send it back
    path = "/api/cloud/" + uuid
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password)
    next_cookie_jar = helper_avi.get_next_cookie_jar(login_response, None, avi_vm_ip, token)
    # response = requests.post(api_endpoint + path, verify=False, headers=headers, cookies=dict(sessionid=login_response.cookies['sessionid']))
    response = requests.put(api_endpoint + path, verify=False, json=default_cloud_details, headers=headers, cookies=next_cookie_jar)
    if response.status_code < 300:
        pmsg.green("Default-Cloud updated with vCenter credentials.")
        return True
    else:
        pmsg.fail("Can't update Cloud credential data: " + str(response.status_code) + ": " + response.text)
    return False


# ##################################################################
# Login and get session ID...
path = "/login"
logged_in = False
exit_code = 1
login_response = requests.post(api_endpoint + path, verify=False, data={'username': avi_username, 'password': avi_password})
if login_response.status_code >= 300:
    pmsg.fail("Can't login to AVI.")
    exit(exit_code)
logged_in = True
token = helper_avi.get_token(login_response, "")

# Try to retrieve the kube_api VIP. We may have to wait a while before it is allocated in AVI after
#  terraform starts to create the supervisor cluster.
response, cloud_details = get_cloud_details(api_endpoint, login_response, avi_username, avi_password, token)
if response.status_code < 300:
    logged_in = True
if cloud_details is not None:
    token = helper_avi.get_token(response, token)
    pmsg.green("Cloud data retrieved OK.")
    pmsg.normal(cloud_details["results"][0]["uuid"])
    if set_cloud_details(api_endpoint, response, cloud_details, avi_vm_ip, avi_username, avi_password, token):
        exit_code = 0
else:
    pmsg.fail("Can't retrieve Cloud data.")

if logged_in:
    helper_avi.logout(api_endpoint, login_response, avi_vm_ip, avi_username, avi_password, token)

exit(exit_code)
