#!/usr/bin/env bash

# Deletes the tfstate files in user_terraform and wm_terraform

rm -f user_terraform/*tfstate*
rm -f wm_terraform/*tfstate*
