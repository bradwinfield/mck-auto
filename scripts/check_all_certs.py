#!/usr/bin/env python3

# Dumps details about all certs and the private keys.
# Arguments: <directory>

# The directory is expected to have subdirectories where each on has files
# *.crt
# *.key

import sys
import os
import helper
import pmsg

if len(sys.argv) < 2:
    pmsg.normal(f'Usage: {sys.argv[0]} <cert parent directory>')
    exit(1)

def has_cert(subdir):
    for file in os.listdir(subdir):
        if 'crt' in file:
            return True
    return False


directory = sys.argv[1]

for subdir in os.listdir(directory):
    path = directory + "/" + subdir
    if os.path.isdir(path) and has_cert(path):
        pmsg.blue(f"\n=========== Examining Certs in {path} ==================================")
        helper.run_a_command("./scripts/check_cert.py " + path)
