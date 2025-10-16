# core/vendors/vendor_cisco.py
from core.vendors.vendor_base import VendorBase

class CiscoDevice(VendorBase):
    def get_interfaces(self):
        return self.ssh.run("show ip interface brief")

    def get_running_config(self):
        return self.ssh.run("show running-config")

    def get_system_health(self):
        # Lấy toàn bộ output trước
        cpu_full_output = self.ssh.run("show processes cpu sorted")
        mem_full_output = self.ssh.run("show memory summary")
        ver_full_output = self.ssh.run("show version")

        # Dùng Python để lọc ra dòng cần thiết
        cpu_line = ""
        for line in cpu_full_output.splitlines():
            if "CPU utilization" in line:
                cpu_line = line
                break
        
        mem_line = ""
        for line in mem_full_output.splitlines():
            if "Processor" in line:
                mem_line = line
                break

        uptime_line = ""
        for line in ver_full_output.splitlines():
            if "uptime is" in line:
                uptime_line = line
                break
        
        # Trả về kết quả đã được xử lý
        return (f"--- System Health ---\n"
                f"CPU: {cpu_line.strip()}\n"
                f"Memory: {mem_line.strip()}\n"
                f"Uptime: {uptime_line.strip()}")
