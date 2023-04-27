#!/usr/bin/env bash

cat << EOF

Perform the following steps manually in AVI before completing the automation.
1. Add the Root & Intermediate certificate (Templates -> Security -> SSL/TLS Certificates)
2. Add the leaf certificate as a Controller Certificate.
3. Change the UI/API so that it uses the new Controller Certificate. (Administration -> System Settings -> Edit)
   a. Change the "SSL/TLS Certificate" by removing the two you see and selecting the new Controller Certificate that you put in.
4. Logout and Login to AVI to make sure it works.

ALTERNATIVELY, you can find the certificate in AVI and put that into the config file so that vCenter can talk to AVI.
See the cert in: Templates -> Security -> SSL/TLS Certificates "System-Default-Portal-Cert"

EOF
