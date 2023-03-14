# Check / Create TKG Admin user
NOTE: This terrform provider does not apparently provide support for a "vsphere_user". This one does not work but is left here as an example for other operations.

# Running terraform

1. Update the file "variables.tfvars"
2. Run thie to generate the state file: $ terraform init
3. Run this to create the plan: $ terraform plan -var-file=variables.tfvars -out user.tfplan
   or: $ terraform plan -var="vsphere_user=tkg-admin@vsphere.local" -var="vsphere_password=Mypassword!" -var="vsphere_server=vc01.h2o-2-7752.h2o.vmware.com"
4. Run this to run the plan and check/create the user: $ terraform apply user.tfplan

