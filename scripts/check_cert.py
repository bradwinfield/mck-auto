#!/usr/bin/env python3

# Dumps details about a cert and the private key.
# Arguments: <directory>

# The directory is expected to have files
# *.crt
# *.key

import sys
import os
import subprocess
import pmsg

if len(sys.argv) < 2:
    pmsg.normal(f'Usage: {sys.argv[0]} <cert directory>')
    exit(1)

directory = sys.argv[1]

for file in os.listdir(directory):
    if '.key' in file:
        key_file_name = directory + "/" + file
    if '.crt' in file:
        cert_file_name = directory + "/" + file

result = subprocess.getoutput(f'openssl x509 -in {cert_file_name} -noout -text | grep -E "Issuer:|Subject:|DNS:"')
pmsg.normal("\nCertificate details =-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
pmsg.normal(cert_file_name)
pmsg.normal(result)

# Get the md5 checksum and compare them...
md5_crt = subprocess.getoutput(f'openssl x509 -noout -modulus -in {cert_file_name} | openssl md5')
md5_key = subprocess.getoutput(f'openssl rsa -noout -modulus -in {key_file_name} | openssl md5')

if md5_crt == md5_key:
    pmsg.green("Certificate and Private key OK.")
else:
    pmsg.fail("Certificate and Private key do not match.")

pmsg.normal(key_file_name)