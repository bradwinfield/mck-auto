#!/usr/bin/env python3

# Create a private key, Certificate Authority, CSR and certificate
import helper
import os
import pmsg

homedir = os.environ["HOME"]

directory = homedir + "/CA"
if not os.path.exists(directory):
    os.mkdir(directory)

cn = "avi.h2o-75-9210.h2o.vmware.com"
#passphrase = "passphrase"
subject = "/C=US/ST=MO/L=STL/O=vmware/OU=PlatformServices/CN=" + cn

private_key_file = directory + "/CAPrivate.key"
root_cert_file = directory + "/CARoot.pem"
my_private_key_file = directory + "/MyPrivate.key"
csr_file = directory + "/MyRequest.csr"
certificate_file = directory + "/certificate.crt"

# passphrase_file = directory + "/passphrase"
# with open(passphrase_file, 'w') as file:
#    file.write(passphrase)

pmsg.blue("Step 1: Create a private key...")
if helper.run_a_command("openssl genrsa -des3 -out " + private_key_file + " 2048") != 0:
    pmsg.fail("Can't create a private key.")
    exit(1)

pmsg.blue("Step 2: Generate the Root Certificate...")
#if helper.run_a_command("openssl req -x509 -new -nodes -key " + private_key_file + " -sha256 -days 365 -out " + root_cert_file + " -subj \"" + subject + "\"") != 0:
if helper.run_a_command("openssl req -x509 -new -nodes -key " + private_key_file + " -sha256 -days 365 -out " + root_cert_file) != 0:
    pmsg.fail("Can't create a Root Certificate.")
    exit(1)

pmsg.blue("Step 3a: Create a personal private key...")
if helper.run_a_command("openssl genrsa -out " + my_private_key_file + " 2048") != 0:
    pmsg.fail("Can't create a Personal Private Key.")
    exit(1)

pmsg.blue("Step 3b: Generate the Certificate Signing Request...")
if helper.run_a_command("openssl req -new -key " + my_private_key_file + " -out " + csr_file) != 0:
    pmsg.fail("Can't create a Personal Private Key.")
    exit(1)

pmsg.blue("Step 4: Generate the Certificate using the CSR...")
if helper.run_a_command("openssl x509 -req -in " + csr_file + " -CA " + root_cert_file + " -CAkey " + private_key_file + " -CAcreateserial -out " + certificate_file + " -days 365 -sha256") != 0:
    pmsg.fail("Can't generate the certificate from the CSR and CAPrivate key.")
    exit(1)

pmsg.green("Certificate created OK.")
pmsg.normal("See " + directory + " for all the files:")
pmsg.normal("CA Private key: " + private_key_file)
pmsg.normal("Root certificate: " + root_cert_file)
pmsg.normal("My personal private key: " + my_private_key_file)
pmsg.normal("CSR: " + csr_file)
pmsg.normal("Certificate: " + certificate_file)
