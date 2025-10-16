from core.ssh_client import SSHClient
from core.vendors.vendor_factory import get_vendor_class

def show_interface_info(device, username, password):
    ssh = SSHClient(device, username, password)
    conn = ssh.connect()
    if not conn:
        return

    VendorClass = get_vendor_class(device["device_type"])
    if not VendorClass:
        print("❌ Chưa hỗ trợ thiết bị loại: {device['device_type']}")
        ssh.disconnect()
        return

    vendor = VendorClass(ssh)
    print("\n--- INTERFACE INFORMATION ---")
    print(vendor.get_interfaces())
    ssh.disconnect()
