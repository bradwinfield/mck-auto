#!/usr/bin/env python3

# This script will create/check 2 certs in AVI
# 1. root/intermediate certificate from "avi_root_certificate"
# 2. controller certificate from "avi_certificate"
# and then the system->ssl for the ui/api is changed to use this controller cert.

import requests
import json
import os
import urllib3
import helper_avi
import pmsg
import pdb

urllib3.disable_warnings()

# Get local variables from environment to make it cleaner looking code.
avi_vm_ip1 = os.environ["avi_vm_ip1"]
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
avi_certificate = os.environ["avi_certificate"]
avi_root_certificate = os.environ["avi_root_certificate"]
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
vsphere_datacenter = os.environ["vsphere_datacenter"]

cert_name = "mck-avi"
root_cert_name = "mck-avi-root"

avi_vm_ip = avi_vm_ip1
if "avi_vm_ip_override" in os.environ.keys():
    avi_vm_ip = os.environ["avi_vm_ip_override"]
api_endpoint = "https://" + avi_vm_ip

def get_root_cert_json(certificate, public_key):
    root_cert_json =  {
        "certificate": {
            "certificate": "-----BEGIN CERTIFICATE-----\nMIIa...nLCZM0pYJ\n-----END CERTIFICATE-----",
            "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBI...Sh/5\nlQIDAQAB\n-----END PUBLIC KEY-----\n",
        },
        "name": "avi01-rootca-2",
    }
    return cert_jsondef get_root_cert_json():

def get_cert_json(certificate: str, passphrase):
    # The certificate needs to be one line where newlines are converted to "\n"...
    cert = certificate.replace(' ', '').replace("\n", '\n')
    cert_json = {
        "certificate": {
            "certificate": cert,
        },
        "key_passphrase": passphrase,
        "name": "avi01-2",
    }
    return cert_json

def get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token):
    # Send a GET request to the API endpoint to retrieve the Default-Cloud details...
    # return json object of config
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password)
    response = requests.get(api_endpoint + path, verify=False, headers=headers, cookies=dict(sessionid=login_response.cookies['sessionid']))

    cloud_details = json.loads(response.text)

    if response.status_code == 200:
        return response, cloud_details
    else:
        pmsg.fail("Error retrieving cloud config: " + str(response.status_code) + response.text)
    return response, None

def put_avi_object(api_endpoint, login_response, obj_details, avi_vm_ip, avi_username, avi_password, token):
    # Update or construct AVI object json... ## SAMPLE ##
    avi_object_details = obj_details["results"][0]
    avi_object_details["vtype"] = "CLOUD_VCENTER"
    uuid = obj_details["uuid"]

    # send it back
    path = "/api/cloud/" + uuid

    # Must set the header and the cookie for a PUT call...
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password)
    cookies = helper_avi.get_next_cookie_jar(login_response, None, avi_vm_ip, token)
    response = requests.put(api_endpoint + path, verify=False, json=obj_details, headers=headers, cookies=cookies)
    return response


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
cert_name_found = False
root_cert_name_found = False
path = "/api/sslkeyandcertificate"
response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if obj_details is not None:
    token = helper_avi.get_token(response, token)

    pdb.set_trace()
    for result in obj_details["results"]:
        if result["name"] == cert_name:
            cert_name_found = True
        if result["name"] == root_cert_name:
            root_cert_name_found = True

    if not root_cert_name_found:
        # create a json for the root cert
        root_cert_json = get_cert_json()
        root_cert_json["name"] = root_cert_name
        # ...
        response = put_avi_object(api_endpoint, login_response, root_cert_json, avi_vm_ip, avi_username, avi_password, token)
        if response.status_code < 300:
            pmsg.green("Root Certificate in AVI OK.")
            exit_code = 0
        else:
            pmsg.fail("Can't POST the Root/Intermediate certificate to AVI." + str(response.status_code) + " " + response.text)

    if not cert_name_found:
        # create a json for the controller certificate
        # AVI wants a certificate, private key and passphrase...
        cert_json = get_cert_json(avi_certificate, private_key, passphrase)
        cert_json["name"] = cert_name
        # ...
        response = put_avi_object(api_endpoint, login_response, cert_json, avi_vm_ip, avi_username, avi_password, token)
        if response.status_code < 300:
            pmsg.green("Client Certificate in AVI OK.")
            exit_code = 0
        else:
            pmsg.fail("Can't POST the client certificate to AVI." + str(response.status_code) + " " + response.text)

pmsg.warning("Not working yet.")
exit(1)

# ##################### PUT AVI Object #############################################
if not cert_name_found:

if logged_in:
    helper_avi.logout(api_endpoint, login_response, avi_vm_ip, avi_username, avi_password, token)

exit(exit_code)
