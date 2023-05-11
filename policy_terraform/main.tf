# see: https://registry.terraform.io/providers/hashicorp/vsphere/latest/docs/resources/vm_storage_policy

variable "vsphere_server" {
  type        = string
  description = "vCenter FQDN."
}
variable "vsphere_username" {
  type        = string
  description = "Admin user in vCenter."
}
variable "vsphere_password" {
  type        = string
  description = "Admin password."
}

terraform {
  required_providers {
    vsphere = {
      version = ">= 2.1.1"
      source = "hashicorp/vsphere"
    }
  }
}

provider "vsphere" {
  vsphere_server = var.vsphere_server
  user           = var.vsphere_username
  password       = var.vsphere_password
  allow_unverified_ssl = true
}

data "vsphere_storage_policy" "tanzu-sp" {
  name = "VM Encryption Policy"
}

output "tanzu-sp" {
  value = data.vsphere_storage_policy.tanzu-sp
}