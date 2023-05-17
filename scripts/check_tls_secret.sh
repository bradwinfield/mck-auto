#!/usr/bin/env bash

# This script will check / create the TLS secret in a namespace
# Inputs:
# - site_name - e.g hlt1, rut1, etc. Provided by the pipeline.
# - namespace_name - The namespace in which you want the TLS secret. e.g. dsr
# - secret_name - The name of the secret in the given namespace.

namespace_name=$1
secret_name=$2

function die {
        >&2 echo "FATAL: ${@:-UNKNOWN ERROR}"
        exit 1
}
 
# We are creating a dsr NameSpace and creating the ingress Secret
cd /usr/src/cloud-development/tanzu-certs/
kubectl get ns ${namespace_name} || kubectl create ns ${namespace_name} || die "Could not create namespace \"dsr\" and namespace does not exist."
kubectl get secret ${secret_name} -n ${namespace_name} || kubectl create secret tls ${secret_name} -n ${namespace_name} \
        --key=<(openssl rsa -in "${site_name}/ingress/${site_name}in.mckesson.com.key.enc" -passin file:keypassword 2>/dev/null) \
        --cert=<(openssl x509 -in "${site_name}/ingress/${site_name}in.mckesson.com.crt"; cat McKesson_Global_RSA4096_SHA256_2022_ICA4.crt) || die "Error creating TLS secret."

echo "Created dsr tls NameSpace and Secret"
