#!/usr/bin/env python3

# Hits the admin-user-setup page in an AVI vm to initialize the admin user.
# This script is not able to change the 'admin' password. Must be done manually
# at this time.

import requests
import pmsg
import urllib3
import os

urllib3.disable_warnings()

avi_user = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
avi_vm_ip1 = os.environ["avi_vm_ip1"]
avi_floating_ip = os.environ["avi_floating_ip"]
dns_servers = os.environ["dns_servers"]
dns_search_domain = os.environ["dns_search_domain"]

default_avi_password = '58NFaGDJm(PJH0G'
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

6. get default-values and parse out the backupconfiguration
backup

###################################################
# 8. do a PUT to change the default admin password...
print("STEP 8 Change default admin password. ################################")
path = "/api/useraccount"
headers["Content-Type"] = "application/json;charset=UTF-8"
headers["Accept"] = "application/json"
headers["referer"] = api_endpoint + "/login"
data = str({"username": "admin", "password": avi_password, "old_password": default_avi_password}).replace("'",'"')
response = requests.put(api_endpoint + path, headers=headers, data=data, cookies=login_response.cookies, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't change the default admin password in AVI. Recommend manual operation. HTTP: " + str(response.status_code))
    exit(1)
next_cookie = get_next_cookie(response, token)
token = get_token(response)
###################################################
# 9a. Get the system configuration:
print("STEP 9a - Get the system configuration..."
path = "/api/systemconfiguration/?include_name=true&join=admin_auth_configuration.remote_auth_configurations.auth_profile_ref"
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get system config data from AVI. HTTP: " + str(response.status_code) + " " + response.text)
    exit(1)
next_cookie = get_next_cookie(response, token)
token = get_token(response)
system_configuration = json.loads(response.text)

##################################################
# 9b. Get the system configuration:
print("STEP 9b - Get the system configuration..."
path = "/api/backupconfiguration/backupconfiguration-4f48934d-1cc3-433e-91e4-4e241616d4b4?include_name=true"
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get system config data from AVI. HTTP: " + str(response.status_code) + " " + response.text)
    exit(1)
next_cookie = get_next_cookie(response, token)
token = get_token(response)
system_configuration = json.loads(response.text)
###################################################
# 9. Create/Enter a passphrase...
print("STEP 9 Create a passphrase")
path = "/api/macrostack"
headers["Content-Type"] = "application/json;charset=UTF-8"
headers["Accept"] = "application/json"
headers["referer"] = api_endpoint + "/"
payload = {
    "data": [
        {
            "data": {
                "url": "https://10.220.30.134/api/backupconfiguration/backupconfiguration-dd61aa76-0553-4dbe-80bf-3f66683199bd#Backup-Configuration",
                "uuid": "backupconfiguration-dd61aa76-0553-4dbe-80bf-3f66683199bd",
                "name": "Backup-Configuration",
                "tenant_ref": "https://10.220.30.134/api/tenant/admin#admin",
                "save_local": True,
                "maximum_backups_stored": 4,
                "remote_file_transfer_protocol": "SCP",
                "backup_passphrase": avi_password
            },
            "method": "PUT",
            "model_name": "backupconfiguration"
        },
        {
            "data": {
                "url": "https://" + avi_floating_ip + "/api/systemconfiguration",
                "uuid": "default",
                "dns_configuration": {
                    "server_list": [
                        {
                            "addr": dns_servers,
                            "type": "V4"
                        }
                    ],
                    "search_domain": dns_search_domain
                }
            },
            "method": "PUT",
            "model_name": "systemconfiguration"
        }
    ]
}
data = str(payload).replace("'", '"')
response = requests.post(api_endpoint + path, headers=headers, data=data, cookies=login_response.cookies, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't change the default admin password in AVI. Recommend manual operation. HTTP: " + str(response.status_code))
    exit(1)
next_cookie = get_next_cookie(response, token)
token = get_token(response)
'''
data_orig = {
  "data": [
    {
      "data": {
        "url": "https://10.220.30.134/api/backupconfiguration/backupconfiguration-dd61aa76-0553-4dbe-80bf-3f66683199bd#Backup-Configuration",
        "uuid": "backupconfiguration-dd61aa76-0553-4dbe-80bf-3f66683199bd",
        "name": "Backup-Configuration",
        "tenant_ref": "https://10.220.30.134/api/tenant/admin#admin",
        "_last_modified": "1681845986736247",
        "save_local": True,
        "maximum_backups_stored": 4,
        "remote_file_transfer_protocol": "SCP",
        "backup_passphrase": "qBO2OA3Rf7e1X@leQdp"
      },
      "method": "PUT",
      "model_name": "backupconfiguration"
    },
    {
      "data": {
        "url": "https://10.220.30.134/api/systemconfiguration",
        "uuid": "default",
        "_last_modified": "1681845985469008",
        "dns_configuration": {
          "server_list": [
            {
              "addr": "10.220.136.2",
              "type": "V4"
            }
          ],
          "search_domain": "h2o-75-9210.h2o.vmware.com"
        },
        "ntp_configuration": {
          "ntp_servers": [
            {
              "server": {
                "addr": "0.us.pool.ntp.org",
                "type": "DNS"
              }
            },
            {
              "server": {
                "addr": "1.us.pool.ntp.org",
                "type": "DNS"
              }
            },
            {
              "server": {
                "addr": "2.us.pool.ntp.org",
                "type": "DNS"
              }
            },
            {
              "server": {
                "addr": "3.us.pool.ntp.org",
                "type": "DNS"
              }
            }
          ],
          "ntp_server_list": [],
          "ntp_authentication_keys": []
        },
        "portal_configuration": {
          "enable_https": True,
          "redirect_to_https": True,
          "enable_http": True,
          "use_uuid_from_input": false,
          "enable_clickjacking_protection": True,
          "allow_basic_authentication": false,
          "password_strength_check": True,
          "disable_remote_cli_shell": false,
          "disable_swagger": false,
          "api_force_timeout": 24,
          "minimum_password_length": 8,
          "sslkeyandcertificate_refs": [
            "https://10.220.30.134/api/sslkeyandcertificate/sslkeyandcertificate-b0b072aa-70e5-423d-a17e-1a0490330643#System-Default-Portal-Cert",
            "https://10.220.30.134/api/sslkeyandcertificate/sslkeyandcertificate-6160adce-f59c-425b-8a57-d0fe83c91a0f#System-Default-Portal-Cert-EC256"
          ],
          "sslprofile_ref": "https://10.220.30.134/api/sslprofile/sslprofile-da1dd6ac-de09-4d99-9b21-48e15299a3a5#System-Standard-Portal"
        },
        "global_tenant_config": {
          "tenant_vrf": false,
          "se_in_provider_context": True,
          "tenant_access_to_provider_se": True
        },
        "email_configuration": {
          "smtp_type": "SMTP_NONE"
        },
        "docker_mode": false,
        "ssh_ciphers": [
          "aes128-ctr",
          "aes256-ctr"
        ],
        "ssh_hmacs": [
          "hmac-sha2-512-etm@openssh.com",
          "hmac-sha2-256-etm@openssh.com",
          "hmac-sha2-512"
        ],
        "default_license_tier": "ENTERPRISE_WITH_CLOUD_SERVICES",
        "secure_channel_configuration": {
          "sslkeyandcertificate_refs": [
            "https://10.220.30.134/api/sslkeyandcertificate/sslkeyandcertificate-2d22c75d-c95d-4de1-9608-be80cc93dff4#System-Default-Secure-Channel-Cert"
          ]
        },
        "welcome_workflow_complete": false,
        "fips_mode": false,
        "enable_cors": false,
        "common_criteria_mode": false,
        "host_key_algorithm_exclude": "",
        "kex_algorithm_exclude": "",
        "mgmt_ip_access_control": {},
        "linux_configuration": {}
      },
      "method": "PUT",
      "model_name": "systemconfiguration"
    }
  ]
}

'''

exit(0)
