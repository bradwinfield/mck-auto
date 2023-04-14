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