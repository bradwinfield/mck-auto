terraform {
  required_providers {
    // Force local binary use, rather than public binary
    namespace-management = {
      version = "0.1"
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

variable "vsphere_datacenter" {
  type        = string
  description = "Datacenter name..."
}
variable "cluster_name" {
  type        = string
  description = "Cluster name."
}
variable "storage_class" {
  type = string
  description = "Name of default storage class/policy"
}
variable "avi_controller_ip" {
  type = string
  description = "IP Address of the AVI controller."
}
variable "avi_certificate" {
  type = string
  description = "AVI Certificate."
}
variable "supervisor_network_starting_ip" {
  type = string
  description = "Starting IP address of Supervisor VMs."
}
variable "supervisor_network_subnet_mask" {
  type = string
  description = "Supervisor network subnet mask."
}
variable "supervisor_network_gateway_ip" {
  type = string
  description = "Supervisor network gateway IP address."
}
variable "dns_servers" {
  type = string
  description = "DNS server IPs or FQDNs comma separated."
}
variable "dns_search_domain" {
  type = string
  description = "DNS search domain."
}
variable "ntp_servers" {
  type = string
  description = "NTP Server IPs or FQDNs comma separated."
}
data "vsphere_datacenter" "dc" {
  name = var.vsphere_datacenter
}

# Converts the vSphere cluster name to its id
data "vsphere_compute_cluster" "fetch" {
  name = var.cluster_name
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_distributed_virtual_switch" "vds" {
  name          = var.distributed_switch
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_distributed_port_group" "supervisor_network" {
  distributed_virtual_switch_uuid = data.vsphere_distributed_virtual_switch.id
  name = var.supervisor_distributed_port_group
}

data "vsphere_distributed_port_group" "workload_network" {
  distributed_virtual_switch_uuid = data.vsphere_distributed_virtual_switch.id
  name = var.workload_distributed_port_group
}

data "vsphere_datastore" "publisher_datastore" {
  name          = var.content_library
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_content_library" "content_library" {
  name            = var.content_library
}

# Enables the Tanzu Supervisor Cluster
resource "namespace-management_cluster" "supervisor" {
  cluster_id = data.vsphere_compute_cluster.fetch.id
  master_storage_policy_id = var.storage_class
  image_storage_policy_id = var.storage_class
  ephemeral_storage_policy_id = var.storage_class
  load_balancer_provider = "AVI"
  load_balancer_id = var.cluster_name
  load_balancer_avi_host = var.avi_controller_ip
  load_balancer_avi_ca_chain = var.avi_certificate
  master_network_ip_assignment_mode = "STATICRANGE"
  master_network_id = data.supervisor_network.id
  master_network_static_starting_address_ipv4 = var.supervisor_network_starting_ip
  master_network_static_subnet_mask = var.supervisor_network_subnet_mask
  master_network_static_gateway_ipv4 = var.supervisor_network_gateway_ip
  master_dns_names = var.dns_servers
  master_dns_search_domain = var.dns_search_domain
  master_ntp_servers = var.ntp_servers
  primary_workload_network_vsphere_portgroup_id = data.workload_network.id
  default_kubernetes_service_content_library_id = data.content_library.id
}

# Only the newly enabled cluster (including the cluster ID)
output "cluster" {
  value = namespace-management_cluster.supervisor
}
