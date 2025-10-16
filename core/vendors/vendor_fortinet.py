# core/vendors/vendor_fortinet.py
from core.vendors.vendor_base import VendorBase

class FortinetDevice(VendorBase):
    def get_interfaces(self):
        return self.ssh.run("get system interface physical")

    def get_running_config(self):
        return self.ssh.run("show full-configuration")

    def get_system_health(self):
        """Lấy thông tin CPU, RAM, Uptime cho thiết bị Fortinet."""
        # Lệnh 'get system performance status' trên FortiOS cung cấp đủ thông tin
        output = self.ssh.run("get system performance status")
        
        # Dùng Python để trích xuất các dòng cần thiết
        cpu_line = ""
        mem_line = ""
        uptime_line = ""

        for line in output.splitlines():
            if "CPU states" in line:
                cpu_line = line
            elif "Memory" in line:
                mem_line = line
            elif "Uptime" in line:
                uptime_line = line

        return (f"--- System Health (Fortinet) ---\n"
                f"{cpu_line.strip()}\n"
                f"{mem_line.strip()}\n"
                f"{uptime_line.strip()}")
