# core/vendors/vendor_fortinet.py
import re
from core.vendors.vendor_base import VendorBase

class FortinetDevice(VendorBase):
    def get_interfaces(self):
        return self.ssh.run("get system interface physical")

    def get_running_config(self):
        return self.ssh.run("show full-configuration")

    def get_system_health(self):
        """
        Lấy và phân tích thông tin CPU, RAM, Uptime cho thiết bị Fortinet.
        Phiên bản cuối cùng, hoạt động chính xác với output của bạn.
        """
        output = self.ssh.run("get system performance status")
        
        # --- Xử lý CPU ---
        cpu_match = re.search(r'CPU states:.*?\s+(\d+)%\s+idle', output)
        cpu_usage = 100 - int(cpu_match.group(1)) if cpu_match else "N/A"
        cpu_line = f"CPU Usage: {cpu_usage}%"

        # --- Xử lý Memory (ĐÃ SỬA) ---
        # Regex mới sẽ tìm con số phần trăm nằm trong dấu ngoặc đơn, ví dụ: (32.9%)
        mem_match = re.search(r'Memory:.*?\((\d+\.?\d*)%\)', output)
        mem_line = "Memory Usage: N/A"
        if mem_match:
            mem_percent = mem_match.group(1)
            mem_line = f"Memory Usage: {mem_percent}%"
        
        # --- Xử lý Uptime ---
        uptime_match = re.search(r'Uptime:\s+(.*)', output, re.IGNORECASE)
        uptime_info = uptime_match.group(1).strip() if uptime_match else "N/A"
        uptime_line = f"Uptime: {uptime_info}"

        return (f"--- System Health (Fortinet) ---\n"
                f"{cpu_line}\n"
                f"{mem_line}\n"
                f"{uptime_line}")

