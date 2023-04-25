#!/usr/bin/env python3

import os
import avi_sdk
from avi_sdk.avi_api import ApiSession

avi_vm_ip = os.environ["avi_vm_ip1"]
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]

# create API session object
api = ApiSession.get_session(avi_vm_ip, avi_username, avi_password, api_version="22.1.3")

# define vCenter credentials object
vc_cred = {
    "name": "vcenter-cred",
    "type": "CREDENTIALS_TYPE_VMWARE_VCENTER",
    "username": vsphere_username,
    "password": vsphere_password,
    "vcenters": [
        {
            "vcenter": vsphere_server,
            "datacenter": vsphere_datacenter,
            "cluster": cluster_name,
            "resource_pool": avi_resource_pool,
            "credential": {
                "username": vcenter_username,
                "password": vcenter_password
            }
        }
    ]
}

# add vCenter credentials to Default-Cloud object
cloud_name = "Default-Cloud"
cloud_obj = api.get_object_by_name("cloud", cloud_name)
cloud_obj['vcenter_configuration']['vcenter_credentials'] = [vc_cred]
api.update_object("cloud", cloud_obj['_id'], cloud_obj)

