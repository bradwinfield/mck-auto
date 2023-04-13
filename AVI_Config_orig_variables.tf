
// Avi Provider variables
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

variable "cluster_name" {
  type    = string
  default = "vc01cl01"
}

#variable "esxi_vm_name" {
#  type    = string
#  default = "vesxi01"
#}

variable "vsphere_username" {
  type = string
  default = "administrator@vsphere.local"
}

variable "vsphere_password" {
  type = string
  default = ""
  sensitive = true
}

variable "vsphere_server" {
  type = string
  # NOTE: Hostname ONLY, no protocol or path
  default = ""
}


variable "avi_management_hostname" {
  type = string
  default = "avi_vm_name1"
}
variable "dns_search_domain" {
  type = string
  default = "example.com"
}
variable "dns_servers" {
  type = string
  default = "10.2.0.1"
}

variable "avi_network" {
  type    = string
  default = ""
}
variable "avi_vm_ip1" {
  type = string
  default = "10.2.0.50"
}
variable "avi_network_ip" {
  type = string
  default = "10.2.0.0"
}
# Start IP range for avi_se instances
# was: avi_management_ip_address_start
variable "avi_se_starting_ip" {
  type = string
  default = "10.2.0.53"
}
# was: avi_management_ip_address_end
variable "avi_se_ending_ip" {
  type = string
  default = "10.2.0.59"
}
# variable "avi_management_subnet_mask_dot" {
variable "avi_subnet_mask" {
  type = string
  default = "255.255.255.224"
}

# The following is an integer but written as a string (Avi provider requirement)
#variable "avi_management_subnet_mask_int" {
#  type = string
#  default = "24"
#}
#variable "avi_management_default_gateway" {
variable "avi_default_gateway" {
  type = string
  default = "10.2.0.1"
}
# TODO support multiple
#variable "avi_ntp_server" {
variable "ntp_server" {
  type = string
  default = "10.2.0.1"
}

# More variables for configuring deployment of Avi:-

# This is used in VM tags for "vm_group_name"
# and has "avi-" prepended
# and has "-controller" or "-se" appended
variable "avi_deployment_name" {
  type = string
  default = "deployment-1"
}

variable "avi_cloud_name" {
  type = string
  default = "Default-Cloud"
}
variable "avi_se_group_name" {
  type = string
  default = "Default-Group"
}

// UNUSED
# variable "avi_management_ssh_key" {
#   type = string
#   default = ""
# }


# Licensing related variables
# Note: if true, requires an Avi Enterprise (not essentials) license
variable "avi_prefer_static_routes" {
  type = bool
  default = true
}

# Avi Data network configuration
variable "avi_data_network_name" {
  type = string
  default = "AviDataNetwork"
}
variable "avi_data_network_network_ipv4" {
  type = string
  default = "10.220.50.32"
}
variable "avi_data_network_start_ipv4" {
  type = string
  default = "10.220.50.33"
}
variable "avi_data_network_end_ipv4" {
  type = string
  default = "10.220.50.61"
}
variable "avi_data_network_subnet_mask_int" {
  type = string
  default = "27"
}
variable "avi_data_network_default_gateway" {
  type = string
  default = "10.220.50.62"
}

# System config elements for confirmation
variable "avi_backup_passphrase" {
  type = string
  default = ""
}