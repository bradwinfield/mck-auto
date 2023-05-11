#!/usr/bin/env bash

cat << EOF

Perform the following steps manually in AVI at https://${avi_floating_ip}/ before completing the automation.
1. Add the Root & Intermediate certificate (Templates -> Security -> SSL/TLS Certificates)
2. Add the leaf certificate as a Controller Certificate.
3. Change the UI/API so that it uses the new Controller Certificate. (Administration -> System Settings -> Edit)
   a. Change the "SSL/TLS Certificate" by removing the two you see and selecting the new Controller Certificate that you put in.
   b. Make sure there is a 'check' in the box "Allow Basic Authentication".
   c. Save your changes by clicking the 'SAVE' button.
4. Logout and Login to AVI to make sure it works. Note that it may take a minute or two
   before the new certificate shows up in the browser address bar. Refresh the browser
   every 10 or 20 seconds until the new certificate shows up.

ALTERNATELY, you MUST create the certificate in AVI (SANS to include the FQDN and all IP Addresses) and put that into the config file so that vCenter can talk to AVI.
See the cert in: Templates -> Security -> SSL/TLS Certificates "System-Default-Portal-Cert"

EOF
