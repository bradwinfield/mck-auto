#!/usr/bin/env python3

# Hits the admin-user-setup page in an AVI vm to initialize the admin user.

import requests
# import os
import pdb
# import re
# import http.cookiejar
import urllib3

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

def get_next_cookie(response):
    token = ""
    avi_sid = ""
    sid = ""
    cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)

    # The sessionid values come from the headers -> set-cookie: <three separate set-cookies>
    if "csrftoken" in cookies_dict.keys():
        token = cookies_dict["csrftoken"]
    if "avi-sessionid" in cookies_dict.keys():
        avi_sid = cookies_dict["avi-sessionid"]
    if "sessionid" in cookies_dict.keys():
        sid = cookies_dict["sessionid"]
    return {"csrftoken": token, "avi-sessionid": avi_sid, "sessionid": sid}

###################################################
# 1. do a GET to the csrftoken...
print("STEP 1 - get token #############################")
pdb.set_trace()
response = requests.get(api_endpoint + "/", verify=False)
pdb.set_trace()
next_cookie = get_next_cookie(response)
token = get_token(response)

###################################################
# 2. do a GET to initial-data?include_name&treat_expired_session_as_unauthenticated=true
print("STEP 2 initial-data?include_name&treat_expired_session_as_unauthenticated=true ###############")
# https://10.220.30.132/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true
headers = {
    "Content-Type": "application/json",
    "x-csrftoken": token,
    "x-avi-version": "22.1.3",
    "x-avi-useragent": "UI"
}
#    "x-avi-tenant": "admin"

response = requests.post(api_endpoint + "/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true", verify=False, cookies=next_cookie)
# response = requests.post(api_endpoint + "/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true", headers=headers, verify=False, cookies=next_cookie)
# response = requests.post(api_endpoint + "/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true", headers=headers, verify=False, cookies=response.cookies)
next_cookie = get_next_cookie(response)
token = get_token(response)

###################################################
# 3. do a POST to login with the default password...
print("STEP 2 login with default pw. #############################")
# https://10.220.30.132/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true
headers = {
    "Content-Type": "application/json",
    "x-csrftoken": token,
    "x-avi-version": "22.1.3",
    "x-avi-useragent": "UI"
}
#    "x-avi-tenant": "admin"

#data = { "username": "admin", "password": default_avi_password }

# response = requests.post(api_endpoint + "/login?include_name=true", headers=headers, verify=False, cookies=next_cookie)
response = requests.post(api_endpoint + "/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true", headers=headers, verify=False, cookies=response.cookies)
next_cookie = get_next_cookie(response)
token = get_token(response)

###################################################
# 3. do a GET to get inital data and invalidate the session...
print("STEP 3 get initial data and unauthenticate the session. #############################")
response = requests.put(api_endpoint + "/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true", cookies=next_cookie)
next_cookie = get_next_cookie(response)
token = get_token(response)

#data = {"username": avi_user, "password": avi_password}

#url = "https://" + avi_vm_ip1 + "/login?include_name=true&username=admin&password=" + avi_password
#url = "https://" + avi_vm_ip1 + "/login?include_name=true"
# Set up the HTTP headers and authentication token

# POST...
#response = requests.post(url, verify=False, cookies=cookies_dict, data=data)

exit(0)
