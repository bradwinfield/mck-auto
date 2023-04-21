#!/usr/bin/env python3

# Temporary shim to change the supervisor_cluster_vip.

import helper
import os

helper.add_env_override(True, "supervisor_cluster_vip", os.environ["10.51.3.10"])
exit(0)
