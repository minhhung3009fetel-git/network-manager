# core/backup_restore.py
import os
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

from core.ssh_client import SSHClient
from core.devices import load_devices
from core.utils import load_credentials, clear_screen
from core.ui import console, print_info, print_success, print_error, print_warning
from core.vendors.vendor_factory import get_vendor_class
from rich.prompt import Prompt

BASE_BACKUP_DIR = "data/backups"

# --- CHỨC NĂNG BACKUP ---
def backup_device_config(device, username, password, backup_dir):
    print_info(f"🔄 Đang backup thiết bị {device['name']} ({device['ip']})...")
    ssh = SSHClient(device, username, password)
    if not ssh.connect(): print_error(f"❌ Không thể kết nối đến {device['name']}."); return
    VendorClass = get_vendor_class(device["device_type"])
    if not VendorClass: print_error(f"❌ Không tìm thấy driver cho {device['device_type']}."); ssh.disconnect(); return
    vendor = VendorClass(ssh); config = vendor.get_running_config(); ssh.disconnect()
    if config:
        hcm_tz = ZoneInfo("Asia/Ho_Chi_Minh"); timestamp = datetime.now(tz=hcm_tz).strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{device['name']}_{timestamp}.cfg"; filepath = os.path.join(backup_dir, filename)
        with open(filepath, "w", encoding='utf-8') as f: f.write(config)
        print_success(f"✅ Backup thành công {device['name']}!")
    else: print_error(f"❌ Backup thất bại cho {device['name']}.")

def backup_all_devices():
    print_info("🚀 Bắt đầu backup toàn bộ hệ thống..."); hcm_tz = ZoneInfo("Asia/Ho_Chi_Minh"); today_str = datetime.now(tz=hcm_tz).strftime("%Y-%m-%d"); daily_backup_dir = os.path.join(BASE_BACKUP_DIR, today_str); os.makedirs(daily_backup_dir, exist_ok=True); print_info(f"📁 Lưu tại: {daily_backup_dir}"); devices = load_devices(); username, password = load_credentials()
    if not devices: print_error("Không có thiết bị."); return
    if not username or not password: print_error("Không tìm thấy credentials."); return
    threads = [];
    for name, info in devices.items(): device_info = {'name': name, **info}; thread = threading.Thread(target=backup_device_config, args=(device_info, username, password, daily_backup_dir)); threads.append(thread); thread.start()
    for thread in threads: thread.join()
    print_success("\n🎉 Backup toàn bộ hệ thống đã hoàn tất!")


# --- CÁC HÀM RESTORE ---
def _find_backup_files(device_name):
    backup_files = []
    for root, _, files in os.walk(BASE_BACKUP_DIR):
        for file in files:
            if file.startswith(f"{device_name}_") and file.endswith(".cfg"):
                backup_files.append(os.path.join(root, file))
    return sorted(backup_files, reverse=True)

def _restore_config_to_device(device, username, password):
    if 'fortinet' in device.get('device_type', '').lower():
        print_warning(f"Tính năng Restore cho thiết bị Fortinet ({device['name']}) hiện chưa được hỗ trợ.")
        print_info("Vui lòng thực hiện thao tác này thủ công trên thiết bị.")
        return

    console.rule(f"[bold yellow]Khôi phục cho: {device['name']}[/bold yellow]")
    backup_files = _find_backup_files(device['name'])
    if not backup_files:
        print_warning(f"Không tìm thấy file backup nào cho {device['name']}."); return
    print_info("Các phiên bản backup có sẵn:")
    for i, f in enumerate(backup_files, 1): print(f"  [{i}] {os.path.basename(f)}")
    try:
        choice = int(input("\nChọn phiên bản để restore (nhập 0 để hủy): ").strip())
        if choice == 0 or choice > len(backup_files): print_info("Đã hủy."); return
        chosen_file = backup_files[choice - 1]
        with open(chosen_file, "r", encoding='utf-8') as f: config_commands = f.read().splitlines()
    except (ValueError, IndexError):
        print_error("Lựa chọn không hợp lệ."); return

    print("\n"); print_warning("!!! CẢNH BÁO NGUY HIỂM !!!"); print_warning(f"Bạn sắp ghi đè cấu hình của [bold red]{device['name']}[/bold red] bằng file [cyan]{os.path.basename(chosen_file)}[/cyan]."); print_warning("Hành động này không thể hoàn tác.")
    confirmation = Prompt.ask("Để xác nhận, vui lòng nhập 'YES' (chữ hoa)")
    if confirmation != "YES": print_info("Đã hủy restore."); return

    print_info(f"🔄 Đang tiến hành restore cho {device['name']}...")
    ssh = SSHClient(device, username, password)
    conn = ssh.connect()
    if not conn: print_error(f"Không thể kết nối đến {device['name']}."); return
    try:
        VendorClass = get_vendor_class(device["device_type"])
        if not VendorClass:
            print_error(f"Không tìm thấy driver cho {device['device_type']}."); ssh.disconnect(); return
        vendor = VendorClass(ssh); output = vendor.restore_config(config_commands)
        print_success("✅ Restore thành công!"); print_info("Output từ thiết bị:"); console.print(output)
    except Exception as e:
        print_error(f"❌ Lỗi khi restore: {e}")
    finally:
        ssh.disconnect()

# --- CÁC HÀM PUBLIC MÀ MENU SẼ GỌI ---
def restore_single_device():
    clear_screen()
    devices = load_devices(); username, password = load_credentials()
    if not (devices and username and password): print_error("Thiếu thông tin thiết bị hoặc credentials."); return
    device_list = list(devices.items())
    for i, (name, info) in enumerate(device_list, 1): print(f" [{i}] {name} ({info['ip']})")
    try:
        choice = int(input("\nChọn thiết bị để restore: ").strip())
        name, info = device_list[choice - 1]
        device_info = {'name': name, **info}
        _restore_config_to_device(device_info, username, password)
    except (ValueError, IndexError):
        print_error("Lựa chọn không hợp lệ.")

def restore_by_branch():
    clear_screen()
    branch_name = input("Nhập tên chi nhánh cần restore (ví dụ: HN, HCM): ").strip().upper()
    if not branch_name: return
    devices = load_devices(); username, password = load_credentials()
    if not (devices and username and password): print_error("Thiếu thông tin thiết bị hoặc credentials."); return
    branch_devices = {name: info for name, info in devices.items() if name.upper().startswith(branch_name)}
    if not branch_devices: print_warning(f"Không tìm thấy thiết bị nào cho chi nhánh {branch_name}."); return
    print_info(f"Sẽ thực hiện restore cho các thiết bị: {', '.join(branch_devices.keys())}"); input("Nhấn Enter để bắt đầu...")
    for name, info in branch_devices.items():
        device_info = {'name': name, **info}
        _restore_config_to_device(device_info, username, password)
        input("\nNhấn Enter để tiếp tục với thiết bị tiếp theo...")

def restore_all():
    clear_screen()
    devices = load_devices(); username, password = load_credentials()
    if not (devices and username and password): print_error("Thiếu thông tin thiết bị hoặc credentials."); return
    print_warning("Bạn sắp thực hiện restore cho TOÀN BỘ hệ thống."); print_info(f"Các thiết bị: {', '.join(devices.keys())}"); input("Nhấn Enter để bắt đầu...")
    for name, info in devices.items():
        device_info = {'name': name, **info}
        _restore_config_to_device(device_info, username, password)
        input("\nNhấn Enter để tiếp tục với thiết bị tiếp theo...")
