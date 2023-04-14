
// Avi Provider variables
variable "avi_controller_ip" {
  type = string
  default = ""
}
variable "avi_username" {
  type = string
  default = ""
}

variable "avi_password" {
  type = string
  default = ""
  sensitive = true
}

variable "vsphere_datacenter" {
  type    = string
  default = "vc01"
}
variable "avi_vm_name1" {}
  type    = string
  default = ""
}
variable "avi_vm_ip1" {}
  type    = string
  default = ""
}
variable "avi_vm_name2" {}
  type    = string
  default = ""
}
variable "avi_vm_ip2" {}
  type    = string
  default = ""
}
variable "avi_vm_name3" {}
  type    = string
  default = ""
}
variable "avi_vm_ip3" {}
  type    = string
  default = ""
}
variable "avi_floating_ip" {
  type    = string
  default = ""
}