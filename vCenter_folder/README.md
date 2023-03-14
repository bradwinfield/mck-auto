# Check / Create vCenter folder

# Running terraform

1. Update the file "variables.tfvars"
2. Run thie to generate the state file: $ terraform init
3. Run this to create the plan: $ terraform plan -var-file=variables.tfvars -out myplan.tfplan
   or: $ terraform plan -var="vcenter_folder=sample_folder"
4. Run this to run the plan and check/create the user: $ terraform apply myplan.tfplan

