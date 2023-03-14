# Check / Create Roles

## Running terraform
Run using the parent folder python function: run_pipeline.py --config_file config.yaml

This run_pipeline script will run terraform for you. The steps it follows is equivalent to:

1. Run this to generate the state file: $ terraform init
2. Run this to create the plan: $ terraform plan -var-file=variables.tfvars -out myplan.tfplan or: $ terraform plan -var="vcenter_folder=sample_folder"
3. Run this to run the plan and check/create the user: $ terraform apply myplan.tfplan