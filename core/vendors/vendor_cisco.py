# core/vendors/vendor_cisco.py
from core.vendors.vendor_base import VendorBase

class CiscoDevice(VendorBase):
    def get_interfaces(self):
        return self.ssh.run("show ip interface brief")

    def get_running_config(self):
        return self.ssh.run("show running-config")

    def get_system_health(self):
        # Kết hợp nhiều lệnh để lấy thông tin
        cpu_output = self.ssh.run("show processes cpu sorted | include CPU")
        mem_output = self.ssh.run("show memory summary | include Processor")
        ver_output = self.ssh.run("show version | include uptime")
        return f"--- System Health ---\nCPU: {cpu_output.strip()}\nMemory: {mem_output.strip()}\nUptime: {ver_output.strip()}"
