variable "vsphere_server" {
  type        = string
  description = "vCenter FQDN."
  default     = ""
}

variable "vsphere_user" {
  type        = string
  description = "Admin user in vCenter."
  default     = ""
}

variable "vsphere_password" {
  type        = string
  description = "Admin password."
  default     = ""
}

provider "vsphere" {
  user           = var.vsphere_user
  password       = var.vsphere_password
  vsphere_server = var.vsphere_server
  allow_unverified_ssl = true
}

data "vsphere_datacenter" "dc" {}

resource "vsphere_folder" "folder" {
  path = "/newfolder"
  datacenter_id = data.vsphere_datacenter.dc.id
  type = "vm"
}

resource "vsphere_folder" "sub_folder" {
  path = "${vsphere_folder.folder.path}/subfolder"
  datacenter_id = data.vsphere_datacenter.dc.id
  type = "vm"
}
