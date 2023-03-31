#!/usr/bin/env python3

# Get additional variables needed by the create_vsphere_namespace.py script.
#
# Additional variables needed but not found in config.yaml are:
# - vsphere_cluster_id
# - content_library_id

import os
import vcenter_api
import pmsg
import helper

# Get server and credentials from the environment...
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
cluster_name = os.environ["cluster_name"]
content_library = os.environ["content_library"]

token = vcenter_api.vcenter_login(vsphere_server, vsphere_username, vsphere_password)

if len(token) < 1:
    pmsg.fail("Can't login to the vCenter API.")
    exit(1)

# Get vsphere_cluster_id...
# curl -k -X GET 'https://vc01.h2o-75-9210.h2o.vmware.com/api/vcenter/cluster?names=vc01cl01' -H 'vmware-api-session-id: 03eae18b8fb3adf5133c602d3eca0e10'| jq -r '.[0].cluster'
apipath = "/api/vcenter/cluster?names=" + cluster_name
json_obj = vcenter_api.api_get(vsphere_server, apipath, token)
if json_obj is not None:
    vsphere_cluster_id = json_obj[0]["cluster"]
    helper.add_env_override(True, "vsphere_cluster_id", json_obj[0]["cluster"])


# Get content library id
# curl -k -X POST 'https://vc01.h2o-75-9210.h2o.vmware.com/api/content/library?action=find' -H 'vmware-api-session-id: 03eae18b8fb3adf5133c602d3eca0e10' -H "Content-Type: application/json" --data '{"name": "vc01cl01-wcp"}'
apipath = "/api/content/library?action=find"
data = {"name": content_library}
bstring = vcenter_api.api_post_returns_content(vsphere_server, apipath, token, data, 200)
if bstring is not None:
    vsphere_cluster_id = bstring.decode('utf-8').strip('[]"')
    helper.add_env_override(False, "content_library_id", vsphere_cluster_id)
