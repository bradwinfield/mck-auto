#!/usr/bin/env bash

# Changes all the config.yaml files found in /usr/src/cloud-development/tanzu-cluster-config/*/config.yaml

USAGE="$0 <variable-name> <new-value>"
if [[ $# -ne 2 ]]; then
    echo $USAGE
    exit 1
fi

cluster_config_dir="/usr/src/cloud-development/tanzu-cluster-config"
cluster_config_dir="$HOME/tanzu-cluster-config"

varname=$1
value=$2
tmp_suffix=$$

echo "Setting ${varname} to \"${value}\""
for config in $(ls $cluster_config_dir/*/config.yaml); do
    mv $config $config.$tmp_suffix
    echo "Updating $config..."
    cat $config.$tmp_suffix | sed "s/^${varname}:.*/${varname}: \"$value\"/" > $config
done

echo "Done."
