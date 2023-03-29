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
variable "vsphere_datacenter" {
  type        = string
  description = "Datacenter name."
}
variable "cluster_name" {
  type        = string
  description = "Cluster name."
}

terraform {
  required_providers {
    // Force local binary use, rather than public binary
    namespace-management = {
      version = ">= 0.1"
      source  = "vmware.com/vcenter/namespace-management"
    }
    vsphere = {
      version = ">= 2.1.1"
      source = "hashicorp/vsphere"
    }
  }
}
provider "namespace-management" {
  vsphere_hostname = var.vsphere_server
  vsphere_username = var.vsphere_username
  vsphere_password = var.vsphere_password
  vsphere_insecure = true
}
provider "vsphere" {
  vsphere_server = var.vsphere_server
  user           = var.vsphere_username
  password       = var.vsphere_password
  allow_unverified_ssl = true
}

variable "datacenter_name" {
  type = string
  description = "Datacenter name"
}

module "clusters" {
  source = "./clusters"
  cluster_name = var.cluster_name
  vsphere_datacenter = var.vsphere_datacenter
}

output "cluster" {
  value = module.clusters.cluster
}
