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

resource "vsphere_role" "TKG-Admin" {
  name = "TKG-Admin"
  role_privileges = ["Cns.Searchable", "Datastore.AllocateSpace", "Datastore.Browse", "Datastore.FileManagement", "Global.DisableMethods", "Global.EnableMethods", "Global.Licenses", "Network.Assign", "Resource.AssignVMToPool", "Sessions.GlobalMessage", "Sessions.ValidateSession", "StorageProfile.View", "VirtualMachine.Config.AddExistingDisk", "VirtualMachine.Config.AddNewDisk", "VirtualMachine.Config.AddRemoveDevice", "VirtualMachine.Config.AdvancedConfig", "VirtualMachine.Config.CPUCount", "VirtualMachine.Config.ChangeTracking", "VirtualMachine.Config.DiskExtend", "VirtualMachine.Config.EditDevice", "VirtualMachine.Config.Memory", "VirtualMachine.Config.RawDevice", "VirtualMachine.Config.RemoveDisk", "VirtualMachine.Config.Settings", "VirtualMachine.Interact.PowerOff", "VirtualMachine.Interact.PowerOn", "VirtualMachine.Inventory.CreateFromExisting", "VirtualMachine.Inventory.Delete", "VirtualMachine.Provisioning.DeployTemplate", "VirtualMachine.Provisioning.DiskRandomRead", "VirtualMachine.Provisioning.GetVmFiles", "VirtualMachine.State.CreateSnapshot", "VirtualMachine.State.RemoveSnapshot", "VApp.Import"]
}

resource "vsphere_role" "AviRole-Global" {
  name = "AviRole-Global"
  role_privileges = ["ContentLibrary.AddLibraryItem", "ContentLibrary.DeleteLibraryItem", "ContentLibrary.UpdateLibraryItem", "ContentLibrary.UpdateSession", "Datastore.AllocateSpace", "Datastore.DeleteFile", "Network.Assign", "Network.Delete", "System.Anonymous", "System.Read", "System.View", "VApp.Import", "VirtualMachine.Config.AddNewDisk"]
}

resource "vsphere_role" "AviRole-Folder" {
  name = "AviRole-Folder"
  role_privileges = ["Folder.Create", "Network.Assign", "Network.Delete", "Resource.AssignVMToPool", "System.Anonymous", "System.Read", "System.View", "Task.Create", "Task.Update", "VApp.ApplicationConfig", "VApp.AssignResourcePool", "VApp.AssignVApp", "VApp.AssignVM", "VApp.Create", "VApp.Delete", "VApp.Export", "VApp.Import", "VApp.InstanceConfig", "VApp.PowerOff", "VApp.PowerOn", "VirtualMachine.Config.AddExistingDisk", "VirtualMachine.Config.AddNewDisk", "VirtualMachine.Config.AddRemoveDevice", "VirtualMachine.Config.AdvancedConfig", "VirtualMachine.Config.CPUCount", "VirtualMachine.Config.DiskExtend", "VirtualMachine.Config.DiskLease", "VirtualMachine.Config.EditDevice", "VirtualMachine.Config.Memory", "VirtualMachine.Config.MksControl", "VirtualMachine.Config.RemoveDisk", "VirtualMachine.Config.Resource", "VirtualMachine.Config.Settings", "VirtualMachine.Interact.DeviceConnection", "VirtualMachine.Interact.PowerOff", "VirtualMachine.Interact.PowerOn", "VirtualMachine.Interact.Reset", "VirtualMachine.Interact.ToolsInstall", "VirtualMachine.Inventory.Create", "VirtualMachine.Inventory.Delete", "VirtualMachine.Inventory.Register", "VirtualMachine.Inventory.Unregister", "VirtualMachine.Provisioning.DeployTemplate", "VirtualMachine.Provisioning.DiskRandomAccess", "VirtualMachine.Provisioning.DiskRandomRead", "VirtualMachine.Provisioning.FileRandomAccess", "VirtualMachine.Provisioning.MarkAsVM"]
}

