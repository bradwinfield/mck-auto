#!/usr/bin/env python3

# Hits the admin-user-setup page in an AVI vm to initialize the admin user.
# This script is not able to change the 'admin' password. Must be done manually
# at this time.

import requests
import pmsg
import urllib3
import pdb

urllib3.disable_warnings()

# avi_user = os.environ["avi_username"]
# avi_password = os.environ["avi_password"]
# avi_vm_ip1 = os.environ["avi_vm_ip1"]

avi_user = "admin"
avi_password = "qBO2OA3Rf7e1X@leQdp"
default_avi_password = '58NFaGDJm(PJH0G'
avi_vm_ip1 = "10.220.30.132"
api_endpoint = "https://" + avi_vm_ip1

def set_cookies(token, sid, avi_sid):
    return {"csrftoken": token, "avi-sessionid": avi_sid, "sessionid": sid}

def get_token(response):
    token = ""
    cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
    if "csrftoken" in cookies_dict.keys():
        token = cookies_dict["csrftoken"]
    return token

def get_next_cookie(response, token):
    avi_sid = ""
    sid = ""
    cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)

    # The sessionid values come from the headers -> set-cookie: <three separate set-cookies>
    if "csrftoken" in cookies_dict.keys():
        new_token = cookies_dict["csrftoken"]
        if len(new_token) > 0:
            token = new_token
    if "avi-sessionid" in cookies_dict.keys():
        avi_sid = cookies_dict["avi-sessionid"]
    if "sessionid" in cookies_dict.keys():
        sid = cookies_dict["sessionid"]
    return_this = {"csrftoken": token, "avi-sessionid": avi_sid, "sessionid": sid}
    pmsg.normal(str(return_this))
    return return_this

###################################################
# 1. do a GET to the csrftoken...
print("STEP 1 - get token #############################")
path = "/"
response = requests.get(api_endpoint + path, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get the csrftoken on inital call to the AVI api. HTTP: " + str(response.status_code))
    exit(1)
next_cookie = get_next_cookie(response, "")
token = get_token(response)

###################################################
# 2. do a GET to initial-data?include_name&treat_expired_session_as_unauthenticated=true
print("STEP 2 initial-data?include_name&treat_expired_session_as_unauthenticated=true ###############")
path = "/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true"
response = requests.get(api_endpoint + path, verify=False, cookies=next_cookie)
if response.status_code > 299:
    pmsg.fail("Can't get config data from AVI api. HTTP: " + str(response.status_code))
    exit(1)
next_cookie = get_next_cookie(response, token)
token = get_token(response)

###################################################
# 3. do a POST to login with the default password...
print("STEP 3 login with default pw. #############################")
#path = "/login?include_name=true"
path = "/login"
headers = {
    "Content-Type": "application/json",
    "Accept-Encoding": "application/json",
    "x-csrftoken": token,
    "x-avi-version": "22.1.3",
    "Referer": api_endpoint + "/"
}

data = {"username": "admin", "password": default_avi_password}

login_response = requests.post(api_endpoint + path, data=data, verify=False)
if login_response.status_code > 299:
    pmsg.fail("Can't login to AVI. HTTP: " + str(login_response.status_code))
    exit(1)
next_cookie = get_next_cookie(login_response, token)
token = get_token(login_response)

###################################################
# 4. do a GET to get inital data and invalidate the session...
print("STEP 4 get initial data and unauthenticate the session. #############################")
path = "/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true"
# update the token in the header...
headers["x-csrftoken"] = token
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get config data from AVI. HTTP: " + str(response.status_code))
    exit(1)
next_cookie = get_next_cookie(response, token)
token = get_token(response)

###################################################
# 5.
print("STEP 5 Switch tenant. #############################")
path = "/api/switch-to-tenant?tenant_name=admin"
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get config data from AVI. HTTP: " + str(response.status_code))
    exit(1)
next_cookie = get_next_cookie(response, token)
token = get_token(response)

###################################################
# 8. do a PUT to change the default admin password...
print("STEP 8 Change default admin password. ################################")
path = "/api/useraccount"
headers["Content-Type"] = "application/json;charset=UTF-8"
headers["Accept"] = "application/json"
headers["referer"] = api_endpoint + "/login"
data = {"username": "admin", "password": avi_password, "old_password": default_avi_password}
pdb.set_trace()
#response = requests.put(api_endpoint + path, headers=headers, data=data, cookies=next_cookie, verify=False)
response = requests.put(api_endpoint + path, headers=headers, data=data, cookies=login_response.cookies, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't change the default admin password in AVI. Recommend manual operation. HTTP: " + str(response.status_code))
    exit(1)
next_cookie = get_next_cookie(response, token)
token = get_token(response)

exit(0)
