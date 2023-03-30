#!/usr/bin/env bash

# Script to prepare the jumpbox with the CLIs (tanzu, kubectl, kapp, ytt, etc.)
# Run this from your home directory.
cd $HOME

echo
echo 'Get the CLI bundles (tanzu, velero) from vmware. Do not bother getting kubectl at this time.'
echo See: https://docs.vmware.com/en/VMware-Tanzu-Kubernetes-Grid/1.6/vmware-tanzu-kubernetes-grid-16/GUID-install-cli.html
echo I am assuming that the files will end up in your Downloads subdirectory.
echo Hit return when done.
read ANS

echo "=================================== Download kubectl vsphere-plugin"
echo "Use your browser to go to your vCenter, navigate to Inventory and find your namespace."
echo "From there, find the "Status" panel. Then click the "Open" link which will lead you"
echo "to downloading the kubectl CLI tools."
echo "Hit return when you have it downloaded."
read ANS

gunzip Downloads/tanzu*.gz
#gunzip Downloads/kubectl*.gz
gunzip Downloads/velero*.gz

echo "==================================== Running apt to get necessary packages..."
sudo apt update
sudo apt install python3-pip -y
sudo apt install git -y
sudo apt install openssh-server -y
sudo apt install curl -y

# install helm this way...
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm


echo "Adding python libraries needed for automation..."
pip3 install pyVmomi
pip3 install jinja2

echo "==================================== Installing 'tanzu' CLI..."
mkdir Downloads/tanzu
tar xvf Downloads/tanzu*.tar -C Downloads/tanzu
sudo install Downloads/tanzu/cli/core/v0.25.4/tanzu-core-linux_amd64 /usr/local/bin/tanzu

tanzu init
tanzu version
tanzu plugin clean
tanzu plugin sync
tanzu plugin list

#echo "==================================== Installing 'kubectl' CLI..."
#chmod ugo+x Downloads/kubectl*.1
#sudo install Downloads/kubectl*.1 /usr/local/bin/kubectl
#kubectl version

echo "==================================== Installing 'ytt' CLI..."
gunzip Downloads/tanzu/cli/ytt*.gz
chmod ugo+x Downloads/tanzu/cli/ytt*.1
sudo install Downloads/tanzu/cli/ytt*.1 /usr/local/bin/ytt
ytt version

echo "==================================== Installing 'kapp' CLI..."
gunzip Downloads/tanzu/cli/kapp*.gz
chmod ugo+x Downloads/tanzu/cli/kapp*.1
sudo install Downloads/tanzu/cli/kapp*.1 /usr/local/bin/kapp
kapp version

echo "==================================== Installing 'kbld' CLI..."
gunzip Downloads/tanzu/cli/kbld*.gz
chmod ugo+x Downloads/tanzu/cli/kbld*.1
sudo install Downloads/tanzu/cli/kbld*.1 /usr/local/bin/kbld
kbld version

echo "==================================== Installing 'imgpkg' CLI..."
gunzip Downloads/tanzu/cli/imgpkg*.gz
chmod ugo+x Downloads/tanzu/cli/imgpkg*.1
sudo install Downloads/tanzu/cli/imgpkg*.1 /usr/local/bin/imgpkg
imgpkg version

echo "==================================== Installing 'kubectl' and the vsphere plugin CLI..."
unzip Downloads/vsphere-plugin.zip
sudo install bin/kubectl /usr/local/bin/kubectl
sudo install bin/kubectl-vsphere /usr/local/bin/kubectl-vsphere
