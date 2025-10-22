# core/ssh_client.py
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

class SSHClient:
    def __init__(self, device, username, password):
        self.device = {
            "device_type": device["device_type"],
            "host": device["ip"],
            "username": username,
            "password": password,
        }
        self.conn = None

    def connect(self):
        try:
            self.conn = ConnectHandler(**self.device)
            self.conn.send_command("terminal length 0")
            return self.conn
        except NetmikoTimeoutException:
            print(f"❌ Timeout: {self.device['host']}")
        except NetmikoAuthenticationException:
            print(f"❌ Sai username/password: {self.device['host']}")
        except Exception as e:
            print(f"❌ Lỗi SSH: {e}")

    def run(self, cmd):
        if not self.conn:
            self.connect()
        return self.conn.send_command(cmd)

    def disconnect(self):
        if self.conn:
            self.conn.disconnect()
            self.conn = None

    def run_config_set(self, commands):
        """Hàm an toàn để gửi một bộ lệnh cấu hình."""
        if not self.conn or not self.conn.is_alive():
            self.connect()
        if self.conn:
            return self.conn.send_config_set(commands)
