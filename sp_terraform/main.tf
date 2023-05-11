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

resource "vsphere_vm_storage_policy" "tanzu-sp" {
  name        = "tanzu-sp"
  description = "Used by TKG Kubernetes workload clusters."

  tag_rules {
    tag_category                 = data.vsphere_tag_category.environment.name
    tags                         = [data.vsphere_tag.production.name]
    include_datastores_with_tags = true
  }
  tag_rules {
    tag_category                 = data.vsphere_tag_category.service_level.name
    tags                         = [data.vsphere_tag.platinum.name]
    include_datastores_with_tags = true
  }
  tag_rules {
    tag_category                 = data.vsphere_tag_category.replication.name
    tags                         = [data.vsphere_tag.replicated.name]
    include_datastores_with_tags = true
  }
}