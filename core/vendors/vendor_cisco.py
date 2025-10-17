# core/vendors/vendor_cisco.py
import re
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

        # --- Xử lý CPU ---
        # Tìm chuỗi "five minutes: X%" và lấy giá trị X
        cpu_match = re.search(r'five minutes: (\d+)%', cpu_full_output)
        cpu_usage = cpu_match.group(1) if cpu_match else "N/A"
        cpu_line = f"CPU Usage: {cpu_usage}%"

        # --- Xử lý Memory ---
        # Tìm dòng bắt đầu bằng "Processor", sau đó lấy 2 cột số đầu tiên (Total và Used)
        mem_match = re.search(r'Processor\s+\S+\s+(\d+)\s+(\d+)', mem_full_output)
        mem_line = "Memory Usage: N/A"
        if mem_match:
            total_mem = int(mem_match.group(1))
            used_mem = int(mem_match.group(2))
            if total_mem > 0:
                mem_percent = (used_mem / total_mem) * 100
                # Chuyển đổi sang MB để dễ đọc
                used_mb = used_mem // (1024 * 1024)
                total_mb = total_mem // (1024 * 1024)
                mem_line = f"Memory Usage: {mem_percent:.2f}% ({used_mb}MB / {total_mb}MB)"
        
        # --- Xử lý Uptime (giữ nguyên nhưng làm sạch) ---
        uptime_match = re.search(r'uptime is (.*)', ver_full_output, re.IGNORECASE)
        uptime_info = uptime_match.group(1) if uptime_match else "N/A"
        uptime_line = f"Uptime: {uptime_info.strip()}"

        # Trả về kết quả đã được định dạng đẹp
        return (f"--- System Health ---\n"
                f"{cpu_line}\n"
                f"{mem_line}\n"
                f"{uptime_line}")

    def restore_config(self, config_commands):
        """Đối với Cisco, send_config_set là đủ."""
        return self.ssh.conn.send_config_set(config_commands)
