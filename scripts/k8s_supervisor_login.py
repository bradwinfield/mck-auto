#!/usr/bin/env python3

# Logs into the TKGs Cluster with the tkg-admin user.

import helper
import os

os.environ["login_user"] = os.environ["tkg_user"]
os.environ["login_password"] = os.environ["tkg_user_password"]

exit(helper.run_a_command("./scripts/k8s_login.py"))
