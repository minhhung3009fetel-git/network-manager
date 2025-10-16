# core/vendors/vendor_base.py
class VendorBase:
    def __init__(self, ssh):
        self.ssh = ssh

    def get_interfaces(self):
        raise NotImplementedError

    def get_running_config(self):
        raise NotImplementedError

    def get_system_health(self):
        """Lấy thông tin tổng quan về CPU, RAM, Uptime."""
        raise NotImplementedError
