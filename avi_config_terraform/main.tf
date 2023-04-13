terraform {
  required_providers {
    avi = {
      # version = ">= 21.1"
      source  = "vmware/avi"
    }
    vsphere = {
      version = ">= 2.1.1"
      source = "hashicorp/vsphere"
    }
  }
}
provider "avi" {
  avi_username   = var.avi_username
  avi_password   = var.avi_password
  # avi_controller = vsphere_virtual_machine.vm[0].default_ip_address
  avi_tenant     = "admin"

  # For after creation by vsphere
  avi_controller = var.avi_vm_ip1

  # Required for Terraform provider not to puke
  # Without this it complains about 'common_criteria' being there (even though false by default) as the terraform provider defaults to v18.8
  avi_version = "22.1.3"
}
data "vsphere_datacenter" "dc" {
  name = var.vsphere_datacenter
}

resource "avi_cluster" "vmware_cluster" {
  name = "cluster-0-1"
  nodes {
    ip {
      type = "V4"
      addr = var.avi_vm_ip2
      name = var.avi_vm_name2
    }
    ip {
      type = "V4"
      addr = var.avi_vm_ip3
      name = var.avi_vm_name3
    }
    virtual_ip = var.avi_floating_ip
  }
}