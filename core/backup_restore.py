# core/backup_restore.py
import os
from datetime import datetime
from zoneinfo import ZoneInfo # <-- 1. IMPORT MODULE MỚI

from core.vendors.vendor_factory import get_vendor_class
from core.ssh_client import SSHClient

BACKUP_DIR = "data/backups"

def backup_device_config(device, username, password):
    """Thực hiện backup cấu hình của một thiết bị."""
    print(f"🔄 Đang backup thiết bị {device['ip']}...")
    os.makedirs(BACKUP_DIR, exist_ok=True)

    ssh = SSHClient(device, username, password)
    if not ssh.connect():
        return

    VendorClass = get_vendor_class(device["device_type"])
    if not VendorClass:
        print(f"❌ Không tìm thấy driver cho {device['device_type']}")
        ssh.disconnect()
        return

    vendor = VendorClass(ssh)
    config = vendor.get_running_config()
    ssh.disconnect()

    if config:
        # 2. SỬA DÒNG NÀY ĐỂ THÊM MÚI GIỜ
        hcm_tz = ZoneInfo("Asia/Ho_Chi_Minh")
        timestamp = datetime.now(tz=hcm_tz).strftime("%Y-%m-%d_%H-%M-%S")
        
        device_name = device['name'] 
        filename = f"{device_name}_{timestamp}.cfg"
        filepath = os.path.join(BACKUP_DIR, filename)

        with open(filepath, "w", encoding='utf-8') as f:
            f.write(config)
        print(f"✅ Backup thành công! Lưu tại: {filepath}")
    else:
        print(f"❌ Backup thất bại cho {device['ip']}")
