#!/usr/bin/env python3

# Sets an environment variable so that we don't clash with this users $HOME/.kube config file(s).

import helper
import os

supervisor_cluster = os.environ["supervisor_cluster"]

kubeconfig_dir = "/tmp/"+supervisor_cluster+"_kubeconfig"
helper.add_env_override(True, "KUBECONFIG", kubeconfig_dir)

# Make sure the directory exists...
if not os.path.exists(kubeconfig_dir):
    os.makedirs(kubeconfig_dir)
