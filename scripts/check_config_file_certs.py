#!/usr/bin/env python3

# Reads the configuration file (Argument 1) and dumps out
# the CN/SANs so you can verify it is what you think.
# Also dumps out the private key details.

import sys
import yaml
import os
import subprocess
import pmsg

cert_file_name = "/tmp/leaf.crt"
key_file_name = "/tmp/private.key"

config_file = sys.argv[1]

with open(config_file, 'r') as cf:
    configs = yaml.safe_load(cf)

# what is the avi_certificate (leaf cert)?
cert_file = open(cert_file_name, "w")
cert_file.writelines(configs["avi_certificate"])
cert_file.close()

result = subprocess.getoutput(f'cat {cert_file_name} | openssl x509 -noout -text | grep -E "Issuer:|Subject:|DNS:"')
pmsg.normal("Certificate details =-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
pmsg.normal(result)

# what is the private key
key_file = open(key_file_name, "w")
key_file.writelines(configs["avi_private_key"])
key_file.close()

md5_crt = subprocess.getoutput(f'openssl x509 -noout -modules -in {cert_file_name}')
md5_key = subprocess.getoutput(f'openssl rsa -noout -modules -in {key_file_name}')

if md5_crt == md5_key:
    pmsg.green("Certificate and Private key OK.")
else:
    pmsg.fail("Certificate and Private key do not match.")

# Clean up
os.remove(cert_file_name)
os.remove(key_file_name)
