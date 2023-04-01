#!/usr/bin/env python3

# This script will print out final messages for the Platform Admin.

import os
import pmsg

vsphere_server = os.environ["vsphere_server"]
vsphere_namespace = os.environ["vsphere_namespace"]
supervisor_cluster = os.environ["supervisor_cluster"]
supervisor_cluster_vip = os.environ["supervisor_cluster_vip"]
workload_cluster = os.environ["workload_cluster"]

pmsg.notice("If there were no errors during the deployment...")
pmsg.blue("The deployment of Supervisor Cluster: " + supervisor_cluster + " (" + supervisor_cluster_vip + ") is complete.")
pmsg.notice("Please make sure that DNS is updated to show " + supervisor_cluster + " resolves to " + supervisor_cluster_vip + ".")
pmsg.normal("vSphere cluster: " + vsphere_server + " is now running the workload cluster: " + workload_cluster + ".")
pmsg.normal("You can log in to the clusters as shown here:")
pmsg.normal("  Supervisor Cluster Login:")
pmsg.blue("kubectl vsphere login --server " + supervisor_cluster_vip + " --vsphere-username <yourloginID> --insecure-skip-tls-verify")
pmsg.normal("  Workload Cluster Login:")
pmsg.blue("kubectl vsphere login --server " + supervisor_cluster_vip + " --vsphere-username <yourloginID> --insecure-skip-tls-verify --tanzu-kubernetes-cluster-namespace " + vsphere_namespace + " --tanzu-kubernetes-cluster-name " + workload_cluster)
