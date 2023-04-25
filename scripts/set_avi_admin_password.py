#!/usr/bin/env python3

# Hits the admin-user-setup page in an AVI vm to initialize the admin user.
# This script is not able to change the 'admin' password. Must be done manually
# at this time.
import requests
import urllib3
import os
import json
import pmsg
import http.cookiejar
import http.cookies
import re
from datetime import datetime

urllib3.disable_warnings()

avi_user = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
avi_vm_ip1 = os.environ["avi_vm_ip1"]
avi_vm_ip2 = os.environ["avi_vm_ip2"]
avi_vm_ip3 = os.environ["avi_vm_ip3"]
avi_floating_ip = os.environ["avi_floating_ip"]
dns_servers = os.environ["dns_servers"]
dns_search_domain = os.environ["dns_search_domain"]

avi_vm_ip = avi_vm_ip1
if "avi_vm_ip_override" in os.environ.keys():
    avi_vm_ip = os.environ["avi_vm_ip_override"]

default_avi_password = '58NFaGDJm(PJH0G'
api_endpoint = "https://" + avi_vm_ip

def get_token(response, token):
    cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
    if "csrftoken" in cookies_dict.keys():
        tok = cookies_dict["csrftoken"]
        if len(tok) > 1:
            token = tok
    return token

def make_cookie(name, value, domain, expires, secure):
    cookie = http.cookiejar.Cookie(
        version=0,
        name=name,
        value=value,
        domain=domain,
        domain_specified=True,
        domain_initial_dot=False,
        secure=secure,
        expires=expires,
        path="/",
        path_specified=True,
        port=None,
        port_specified=False,
        discard=False,
        comment=None,
        comment_url=None,
        rest={'HttpOnly': None, 'SameSite': 'None'}
    )
    return cookie

def get_next_cookie_jar(response, last_cookie_jar):
    if last_cookie_jar is None:
        cookie_jar = http.cookiejar.CookieJar()
    else:
        cookie_jar = last_cookie_jar

    # And update the cookie jar with any 'Set-Cookie' values
    sch = response.headers.get('Set-Cookie')
    if len(sch) > 20:

        # First, substitute the commas with '#' that follow the day-of-week name (Sun, -> Sun#). Then, split on comma.
        set_cookie_header = re.sub('expires=(\w{3}),', 'expires=\\1#', sch)
        parts = re.split(',', set_cookie_header)
        for cookie in parts:
            cname = ""
            cvalue = ""
            cexpires = ""
            csecure = False

            cookie_parts = re.split(';', cookie)
            for cookie_part_value in cookie_parts:
                if "=" in cookie_part_value:
                    nm, value = re.split('=', cookie_part_value)
                else:
                    nm = cookie_part_value
                    value = None
                name = nm.strip().lower()
                if name == "max-age":
                    continue
                if re.search('csrftoken|sessionid', name):
                    cname = name
                    cvalue = value
                    continue
                if name == "secure":
                    csecure = True
                    continue
                if name == "expires":
                    cexpires = re.sub('#', ',', value)
                    if re.match('\w+, \d+', cexpires):
                        cexpires = str(datetime.strptime(cexpires, '%a, %d-%b-%Y %H:%M:%S %Z').timestamp()).split('.')[0]

            a_set_cookie = make_cookie(name=cname, value=cvalue, domain=avi_vm_ip, expires=cexpires, secure=csecure)
            cookie_jar.set_cookie(a_set_cookie)
    return cookie_jar


###################################################
# pmsg.normal("STEP 1 - GET token from " + api_endpoint + "#############################")
path = "/"
response = requests.get(api_endpoint + path, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get the csrftoken on inital call to the AVI api. HTTP: " + str(response.status_code) + response.text)
    exit(1)
token = get_token(response, "")
next_cookie_jar = get_next_cookie_jar(response, None)
###################################################
# pmsg.normal("STEP 2 GET initial-data?include_name&treat_expired_session_as_unauthenticated=true ###############")
path = "/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true"
response = requests.get(api_endpoint + path, verify=False, cookies=next_cookie_jar)
if response.status_code > 299:
    pmsg.fail("Can't get config data from AVI api. HTTP: " + str(response.status_code) + response.text)
    exit(1)
token = get_token(response, token)
next_cookie_jar = get_next_cookie_jar(response, next_cookie_jar)

###################################################
# pmsg.normal("STEP 3 POST login with default pw. #############################")
path = "/login?include_name=true"
headers = {
    "Content-Type": "application/json",
    "Accept-Encoding": "application/json",
    "x-csrftoken": token,
    "x-avi-version": "22.1.3",
    "Referer": api_endpoint + "/"
}
data = {"username": "admin", "password": default_avi_password}

response = requests.post(api_endpoint + path, json=data, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't login to AVI. HTTP: " + str(response.status_code) + response.text)
    pmsg.fail("Recommend manual set of AVI password.")
    pmsg.underline(api_endpoint + "/")
    exit(1)
token = get_token(response, token)
next_cookie_jar = get_next_cookie_jar(response, next_cookie_jar)

# newcookies = re.sub(r"expires=(...),", "expires=\\1#", cookie)
# cookies_list = newcookies.split(', ')
# put the found cookies into a dictionary where the name is csrftoken, sessionid, avi-sessionid
# and the value is the rest of the stuff. And replace the expires=...# back to a expires=...,
# and use in next requests ( ... , cookies=cookie_dict)

###################################################
# 4. do a GET to get inital data and invalidate the session...
# pmsg.normal("STEP 4 get initial data and unauthenticate the session. #############################")
path = "/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true"
# update the token in the header...
headers["x-csrftoken"] = token
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get config data from AVI. HTTP: " + str(response.status_code) + response.text)
    exit(1)
token = get_token(response, token)
next_cookie_jar = get_next_cookie_jar(response, next_cookie_jar)
cookie = response.headers.get('Set-Cookie')
###################################################
# 5.
# pmsg.normal("STEP 5 Switch tenant. #############################")
path = "/api/switch-to-tenant?tenant_name=admin"
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get config data from AVI. HTTP: " + str(response.status_code) + response.text)
    exit(1)
token = get_token(response, token)
next_cookie_jar = get_next_cookie_jar(response, next_cookie_jar)

###################################################
# 6. get default-values and parse out the backupconfiguration
# pmsg.normal("STEP 6 getting the backup configuration uuid")
path = "/api/default-values?include_name"
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get config data from AVI. HTTP: " + str(response.status_code) + response.text)
    exit(1)
token = get_token(response, token)
next_cookie_jar = get_next_cookie_jar(response, next_cookie_jar)
json_obj = json.loads(response.text)
backupid = json_obj["default"]["backupconfiguration"][0]
# pmsg.normal("Backup Configuration: " + backupid)

###################################################
# 7. GET controller-inventory
# pmsg.normal("STEP 7 GET controller-inventory.")
path = "/api/controller-inventory/?include=config,faults&include_name=true"
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get controller inventory data from AVI. HTTP: " + str(response.status_code) + response.text)
    exit(1)

###################################################
# 8. do a PUT to change the default admin password...
# pmsg.normal("STEP 8 Change default admin password. ################################")
path = "/api/useraccount"
headers["Content-Type"] = "application/json;charset=UTF-8"
headers["Accept"] = "application/json"
headers["referer"] = api_endpoint + "/login"
data = {"username": "admin", "password": avi_password, "old_password": default_avi_password}
response = requests.put(api_endpoint + path, headers=headers, json=data, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't change the default admin password in AVI. Recommend manual operation. HTTP: " + str(response.status_code) + response.text)
    exit(1)
token = get_token(response, token)
next_cookie_jar = get_next_cookie_jar(response, next_cookie_jar)

###################################################
# 9a. Get the system configuration:
# pmsg.normal("STEP 9a - Get the system configuration...")
path = "/api/systemconfiguration/?include_name=true&join=admin_auth_configuration.remote_auth_configurations.auth_profile_ref"
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get system config data from AVI. HTTP: " + str(response.status_code) + " " + response.text)
    exit(1)
system_config_payload = json.loads(response.text)
system_config_payload["dns_configuration"] = {"server_list": [{"addr": dns_servers, "type": "V4"}], "search_domain": dns_search_domain}
system_config_payload["email_configuration"] = {"smtp_type": "SMTP_NONE"}
system_config_payload["ntp_configuration"]["ntp_server_list"] = []
system_config_payload["ntp_configuration"]["ntp_authentication_keys"] = []
system_config_payload["mgmt_ip_access_control"] = {}
system_config_payload["linux_configuration"] = {}

##################################################
# 9b. Get the backup configuration payload
# pmsg.normal("STEP 9b - Get the backup configuration payload...")
path = "/api/backupconfiguration/" + backupid + "?include_name=true"
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get system config data from AVI. HTTP: " + str(response.status_code) + " " + response.text)
    exit(1)
backup_payload = json.loads(response.text)
backup_payload["backup_passphrase"] = os.environ["vsphere_password"]
bc_cookies = response.cookies

###################################################
# 9c. Create/Enter a passphrase...
# pmsg.normal("STEP 9c Create a passphrase")
path = "/api/macrostack"
headers = response.headers
headers["content-type"] = "application/json;charset=UTF-8"
headers["origin"] = api_endpoint
headers["referer"] = api_endpoint + "/"
headers["x-avi-tenant"] = "admin"
headers["x-avi-useragent"] = "UI"
headers["x-avi-version"] = "22.1.3"
headers["x-csrftoken"] = token
headers["accept"] = "application/json, text/plain, */*"
payload = {
    "data": [
        {
            "data": backup_payload,
            "method": "PUT",
            "model_name": "backupconfiguration"
        },
        {
            "data": system_config_payload,
            "method": "PUT",
            "model_name": "systemconfiguration"
        }
    ]
}
data = json.dumps(payload)
headers["content-length"] = str(len(data))
response = requests.post(api_endpoint + path, headers=headers, data=data, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't change the Passphrase/DNS/Domain in AVI. Recommend manual operation. HTTP: " + str(response.status_code) + response.text)
    pmsg.fail("Recommend manual set of AVI passphrase.")
    pmsg.underline(api_endpoint + "/")
    exit(1)
pmsg.green("AVA admin password/passphrase OK.")

exit(0)
