# core/vendors/vendor_fortinet.py
from core.vendors.vendor_base import VendorBase

class FortinetDevice(VendorBase):
    def get_interfaces(self):
        return self.ssh.run("get system interface physical")

    def get_running_config(self):
        return self.ssh.run("show full-configuration")
