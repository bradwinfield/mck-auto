#!/usr/bin/env python3

# Check for storage policy; create it if it is missing in vCenter.

import os
import pmsg
import helper
import vsphere_mob
from pyVmomi import pbm, VmomiSupport, vim
import argparse
import pdb
import cli
import ssl
import service_instance

# Get server and credentials from the environment...
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
vsphere_datacenter = os.environ["vsphere_datacenter"]
cluster_name = os.environ["cluster_name"]
storage_class = os.environ["storage_class"]

# retrieve SPBM API endpoint
def get_pbm_connection(vpxd_stub):
    from http import cookies
    import pyVmomi
    session_cookie = vpxd_stub.cookie.split('"')[1]
    http_context = VmomiSupport.GetHttpContext()
    cookie = cookies.SimpleCookie()
    cookie["vmware_soap_session"] = session_cookie
    http_context["cookies"] = cookie
    VmomiSupport.GetRequestContext()["vcSessionCookie"] = session_cookie
    hostname = vpxd_stub.host.split(":")[0]

    context = None
    if hasattr(ssl, "_create_unverified_context"):
        context = ssl._create_unverified_context()
    pbm_stub = pyVmomi.SoapStubAdapter(
        host=hostname,
        version="pbm.version.version1",
        path="/pbm/sdk",
        poolSize=0,
        sslContext=context)
    pbm_si = pbm.ServiceInstance("ServiceInstance", pbm_stub)
    pbm_content = pbm_si.RetrieveContent()

    return pbm_si, pbm_content


# Connect to SPBM Endpoint
args = argparse.Namespace()
args.host = vsphere_server
args.port = 443
args.user = vsphere_username
args.password = vsphere_password
args.disable_ssl_verification = True

si = service_instance.connect(args)
pbm_si, pbm_content = get_pbm_connection(si._stub)

pm = pbm_content.profileManager
profile_ids = pm.PbmQueryProfile(
    resourceType=pbm.profile.ResourceType(resourceType="STORAGE"),
    profileCategory="REQUIREMENT"
)

profiles = []
if len(profile_ids) > 0:
    profiles = pm.PbmRetrieveContent(profileIds=profile_ids)

for profile in profiles:
    if profile.name == storage_class:
        pmsg.green ("Storage profile in vSphere OK.")
        print(profile)
        exit(0)

# If I get here, the storage profile does not exist.
pmsg.fail("Storage profile in vSphere not found.")
exit(1)
