# modules/system_health.py
from core.ssh_client import SSHClient
from core.vendors.vendor_factory import get_vendor_class

def show_system_health(device, username, password):
    ssh = SSHClient(device, username, password)
    if not ssh.connect():
        return

    VendorClass = get_vendor_class(device["device_type"])
    if not VendorClass:
        print(f"❌ Chưa hỗ trợ thiết bị này")
        ssh.disconnect()
        return

    vendor = VendorClass(ssh)
    health_info = vendor.get_system_health()
    print(health_info)
    ssh.disconnect()
