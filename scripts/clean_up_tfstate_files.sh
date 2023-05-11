#!/usr/bin/env bash

# Deletes the tfstate files in all terraform (site_terraform)
# declare -a tdirs=("user_terraform" "wm_terraform" "avi_controller_terraform" "avi_config_terraform" "policy_terraform")

# for dir in "${tdirs[@]}"
# do
#    rm -rf site_terraform/$site_name/$dir
# done

rm -rf site_terraform/*
find . -type f|grep -E '\.terra' |xargs rm