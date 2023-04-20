#!/usr/bin/env bash

# Deletes the tfstate files in all terraform (site_terraform)
declare -a tdirs=("user_terraform" "wm_terraform" "avi_controller_terraform" "avi_config_terraform")

for dir in "${tdirs[@]}"
do
    rm -f site_terraform/$site_name/$dir/*tfstate*
    rm -rf site_terraform/$site_name/$dir/.terraform*
    rm -rf site_terraform/$site_name/$dir/*.tfplan
done
