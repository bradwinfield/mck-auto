# Enable Workload Management
wm_terraform
Abort on Error

# Get the Supervisor Cluster VIP...
# This step will attempt to get the VIP for about 30 minutes giving AVI time to allocate the VIP.
get_kube_api_vip.py

# Try to login to the supervisor cluster
# This next step will try for about 20 minutes to give the supervisor cluster time to fully come up.
set_kubeconfig.py
k8s_supervisor_login_admin.py
Abort now if we can not login to the supervisor cluster

# Create the vSphere namespace (but first get some vCenter object IDs)...
env_for_create_ns.py
create_vsphere_namespace.py

# Step to create workload cluster (needs get_kube_api_vip.py)
k8s_supervisor_login_admin.py
tkcclustercreate.py
k8s_cluster_login.py
Abort now if we can not login to the workload cluster

# Steps to complete workload cluster (needs k8s_cluster_login.py & get_kube_api_vip.py)
check_sc.py
check_kapp.py
tanzu_package.py
cert-manager.py
check_contour.py
check_cluster_rb.py
check_fluentbit.py
check_prisma.sh

# Create and publish storage policy on workload with desired Reclaimpolicy and bind mode
create-local-sc.py

# Smoke test
test_ingress.py

print_final_messages.py

# End

