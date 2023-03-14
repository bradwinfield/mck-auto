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
}

resource "vsphere_user" "new_user" {
  username = "tkg-admin@vsphere.local"
  password = "Mypassword!"
  role     = "administrator" # Change this to the desired role for the user
}

