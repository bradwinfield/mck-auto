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

urllib3.disable_warnings()

# Get local variables from environment to make it cleaner looking code.
avi_floating_ip = os.environ["avi_floating_ip"]
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
avi_certificate = os.environ["avi_certificate"]
avi_root_certificate = os.environ["avi_root_certificate"]
avi_private_key = os.environ["avi_private_key"]
avi_passphrase = os.environ["avi_passphrase"]

if "avi_controller_cert_name" in os.environ.keys():
    cert_name = os.environ["avi_controller_cert_name"]
else:
    cert_name = "avi-controller"

if "avi_root_cert_name" in os.environ.keys():
    root_cert_name = os.environ["avi_root_cert_name"]
else:
    root_cert_name = "avi-root"

avi_vm_ip = avi_floating_ip
if "avi_vm_ip_override" in os.environ.keys():
    avi_vm_ip = os.environ["avi_vm_ip_override"]
api_endpoint = "https://" + avi_vm_ip

def get_root_cert_json(certificate):
    root_cert_json = {
        "certificate": {
            "certificate": certificate
        }
    }
    return root_cert_json

def get_cert_json(certificate, private_key, passphrase):
    # The certificate needs to be one line where newlines are converted to "\n"...
    cert_json = {
        "certificate": {
            "certificate": certificate,
        },
        "key_passphrase": passphrase,
        "key": private_key,
        "key_base64": False,
        "certificate_base64": False,
        "import_key_to_hsm": False
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

def post_avi_object(api_endpoint, path, login_response, obj_details, avi_vm_ip, avi_username, avi_password, token):
    # Must set the header and the cookie for a PUT call...
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password)
    cookies = helper_avi.get_next_cookie_jar(login_response, None, avi_vm_ip, token)
    response = requests.post(api_endpoint + path, verify=False, json=obj_details, headers=headers, cookies=cookies)
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
root_status_code = 1
controller_status_code = 1

path = "/api/sslkeyandcertificate"
response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if obj_details is not None:
    token = helper_avi.get_token(response, token)
    for result in obj_details["results"]:
        if result["name"] == cert_name:
            cert_name_found = True
        if result["name"] == root_cert_name:
            root_cert_name_found = True

    if root_cert_name_found:
        pmsg.green("Intermediate+Root Certificates OK.")
        root_status_code = 0
    else:
        # create a json for the intermediate + root certificates.
        root_cert_json = get_root_cert_json(avi_root_certificate)
        root_cert_json["name"] = root_cert_name

        response = post_avi_object(api_endpoint, path, login_response, root_cert_json, avi_vm_ip, avi_username, avi_password, token)
        if response.status_code < 300:
            pmsg.green("Intermediate and Root Certificates in AVI OK.")
            root_status_code = 0
        else:
            pmsg.fail("Can't POST the Root/Intermediate certificate to AVI." + str(response.status_code) + " " + response.text)

    if cert_name_found:
        pmsg.green("Controller (client/leaf) Certificate OK.")
        controller_status_code = 0
    else:
        # create a json for the controller certificate
        # AVI wants a certificate, private key and passphrase...
        cert_json = get_cert_json(avi_certificate, avi_private_key, avi_passphrase)
        cert_json["name"] = cert_name

        response = post_avi_object(api_endpoint, path, login_response, cert_json, avi_vm_ip, avi_username, avi_password, token)
        if response.status_code < 300:
            pmsg.green("Controller Certificate in AVI OK.")
            controller_status_code = 0
        else:
            pmsg.fail("Can't POST the client certificate to AVI." + str(response.status_code) + " " + response.text)
else:
    pmsg.fail("Can't retrieve certificates from AVI. Recommend: validate certs manually.")
exit(exit_code)
