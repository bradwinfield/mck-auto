#!/usr/bin/env python3

# Check to see if the distribution center config file is complete.

import sys
import os
import pmsg
import yaml

config_file = "config.yaml"

if len(sys.argv) < 2:
    pmsg.normal(f'Usage: {sys.argv[0]} <site config file name>')
    exit(1)

site_config_file = sys.argv[1]

if not os.path.exists(config_file):
    config_file = "../config.yaml"

with open(config_file, 'r') as cf:
    configs = yaml.safe_load(cf)
with open(site_config_file, 'r') as scf:
    site_configs = yaml.safe_load(scf)

nmissing = 0

for key in configs.keys():
    if key not in site_configs.keys():
        pmsg.warning(f'Missing key "{key}" in {site_config_file}.')
        nmissing += 1

if nmissing > 0:
    pmsg.fail(f'{nmissing} argument(s) missing in config file: {site_config_file}.')
else:
    pmsg.green("Config file OK.")
