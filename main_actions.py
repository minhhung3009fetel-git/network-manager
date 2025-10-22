# main_actions.py
import os
import getpass

from core.devices import load_devices, list_devices, add_device, delete_device
from core.utils import clear_screen, load_credentials, is_device_reachable
from core.ui import console, print_info, print_error, print_warning, print_success, Panel
from core.backup_restore import restore_single_device, restore_by_branch, restore_all, backup_device_config, BASE_BACKUP_DIR
from core.vendors.vendor_factory import get_vendor_class
from modules.system_health import show_system_health
from modules.interface_info import show_interface_info
from modules import web_filter

def menu_device_manager():
    """Menu con để quản lý danh sách thiết bị."""
    while True:
        clear_screen()
        console.rule("[bold green]Quản lý Danh sách Thiết bị[/bold green]")
        print(" [1] Liệt kê thiết bị")
        print(" [2] Thêm thiết bị mới")
        print(" [3] Xóa thiết bị")
        print("\n [0] Quay lại")
        choice = input("\nChọn chức năng: ").strip()
        if choice == '1': list_devices(); input("\nNhấn Enter...")
        elif choice == '2': add_device(); input("\nNhấn Enter...")
        elif choice == '3': delete_device(); input("\nNhấn Enter...")
        elif choice == '0': break
        else: print_error("Lựa chọn không hợp lệ."); input("\nNhấn Enter...")

def menu_restore():
    """Menu con cho các chức năng Restore."""
    while True:
        clear_screen()
        console.rule("[bold red]Khôi phục Cấu hình (Restore)[/bold red]")
        print(" [1] Restore một thiết bị")
        print(" [2] Restore theo chi nhánh")
        print(" [3] Restore toàn bộ hệ thống")
        print("\n [0] Quay lại")
        choice = input("\nChọn chức năng: ").strip()
        if choice == '1': restore_single_device(); input("\nNhấn Enter...")
        elif choice == '2': restore_by_branch(); input("\nNhấn Enter...")
        elif choice == '3': restore_all(); input("\nNhấn Enter...")
        elif choice == '0': break
        else: print_error("Lựa chọn không hợp lệ."); input("\nNhấn Enter...")

def open_ssh_terminal():
    """Hiển thị danh sách thiết bị và mở một phiên SSH tương tác."""
    clear_screen()
    console.rule("[bold magenta] Mở Terminal SSH Trực tiếp [/bold magenta]")
    
    devices = load_devices()
    if not devices:
        print_warning("Chưa có thiết bị nào trong danh sách."); return
        
    device_list = list(devices.items())

    for i, (name, info) in enumerate(device_list, 1):
        print(f" [{i}] {name} ({info['ip']})")

    try:
        choice = int(input("\nChọn thiết bị để kết nối SSH (nhập 0 để hủy): ").strip())
        if choice == 0: return
        if not (0 < choice <= len(device_list)):
            print_error("Lựa chọn không hợp lệ."); return

        name, info = device_list[choice - 1]
        device_ip = info['ip']

        username, _ = load_credentials()
        if not username:
            print_warning("Không tìm thấy username trong file .env. Vui lòng nhập thủ công.")
            username = input("Nhập username: ").strip()
        if not username: print_info("Đã hủy."); return

        # --- THAY ĐỔI DUY NHẤT Ở DÒNG DƯỚI ĐÂY ---
        # Thêm tùy chọn -o KexAlgorithms để cho phép thuật toán cũ
        command = (
            f"ssh -o KexAlgorithms=+diffie-hellman-group14-sha1 "
            f"-o HostKeyAlgorithms=+ssh-rsa {username}@{device_ip}"
        )
        print_info(f"\nĐang mở phiên SSH tới {name}... (gõ 'exit' trong cửa sổ mới để quay lại menu)")
        input("Nhấn Enter để tiếp tục...")
        
        clear_screen()
#        os.system(command)
        exit_code = os.system(command)
        print_info(f"\nPhiên SSH đã kết thúc với mã thoát: {exit_code}")
        input("\nNhan Enter de tiep tuc")

    except (ValueError, IndexError):
        print_error("Lựa chọn không hợp lệ.")

def _select_and_run_single_action(action_name):
    """Hàm chung để chọn 1 thiết bị và chạy 1 hành động."""
    clear_screen(); console.rule(f"[bold yellow]Chọn thiết bị[/bold yellow]"); devices = load_devices()
    if not devices: print_warning("Chưa có thiết bị."); return
    device_list = list(devices.items());
    for i, (name, info) in enumerate(device_list, 1): print(f" [{i}] {name} ({info['ip']})")
    try:
        choice = int(input("\nChọn thiết bị: ").strip()); name, info = device_list[choice - 1]; device_info = {'name': name, **info}
        username, password = load_credentials()
        if not (username and password): print_error("Không tìm thấy credentials."); return
        
        if action_name == 'show_interfaces': show_interface_info(device_info, username, password)
        elif action_name == 'show_health': show_system_health(device_info, username, password)
        elif action_name == 'backup_single': 
            os.makedirs(BASE_BACKUP_DIR, exist_ok=True)
            backup_device_config(device_info, username, password, BASE_BACKUP_DIR)
        else: print_error("Hành động không xác định.")
    except (ValueError, IndexError): print_error("Lựa chọn không hợp lệ.")

def menu_interaction():
    """Menu con cho Tương tác Trực tiếp."""
    while True:
        clear_screen()
        console.rule("[bold magenta]TƯƠNG TÁC TRỰC TIẾP[/bold magenta]")
        print(" [1] Mở Terminal SSH trực tiếp")
        print(" [2] Xem thông tin Interfaces")
        print(" [3] Kiểm tra System Health")
        print(" [4] Backup một thiết bị")
        print("\n [0] Quay lại")
        choice = input("\nChọn chức năng: ").strip()
        if choice == '1': open_ssh_terminal();
        elif choice == '2': _select_and_run_single_action('show_interfaces'); input("\nNhấn Enter...")
        elif choice == '3': _select_and_run_single_action('show_health'); input("\nNhấn Enter...")
        elif choice == '4': _select_and_run_single_action('backup_single'); input("\nNhấn Enter...")
        elif choice == '0': break
        else: print_error("Lựa chọn không hợp lệ.");

def menu_web_filter():
    """Menu quản lý Policy Lọc Web (đã sửa lỗi)."""
    clear_screen()
    console.rule("[bold blue]🛡️ Quản lý Policy Lọc Web[/bold blue]")
    
    devices = load_devices()
    firewalls = {name: info for name, info in devices.items() if 'fortinet' in info['device_type']}
    if not firewalls: print_warning("Không tìm thấy thiết bị Fortinet nào."); return

    fw_list = list(firewalls.items())
    for i, (name, _) in enumerate(fw_list, 1): print(f" [{i}] {name}")
    try:
        choice = int(input("\nChọn Firewall để cấu hình: ").strip())
        name, info = fw_list[choice - 1]
        target_fw = {'name': name, **info}
    except (ValueError, IndexError):
        print_error("Lựa chọn không hợp lệ."); return

    username, password = load_credentials()
    from core.ssh_client import SSHClient
    ssh = SSHClient(target_fw, username, password)
    if not ssh.connect(): return

    while True:
        clear_screen()
        console.rule(f"[bold blue]📜 Policy trên {target_fw['name']}[/bold blue]")
        rules = web_filter.get_rules(ssh)
        web_filter.display_rules_table(rules)
        
        print("\n--- MENU POLICY ---")
        print(" [1] Thêm Rule mới"); print(" [2] Kích hoạt/Vô hiệu hóa Rule"); print(" [3] Xóa Rule")
        print("\n [0] Quay lại")
        choice = input("\nChọn chức năng: ").strip()

        if choice == '1':
            url = input("Nhập trang web cần xử lý (ví dụ: tiktok.com): ").strip()
            action = input("Chọn hành động (block/allow) [mặc định: block]: ").strip().lower() or "block"
            if url: web_filter.add_rule(ssh, url, action, "enable")
        elif choice == '2':
            try:
                rule_id_str = input("Nhập ID của rule cần thay đổi trạng thái: ").strip()
                rule_to_toggle = next(r for r in rules if r['id'] == rule_id_str)
                web_filter.toggle_rule_status(ssh, rule_to_toggle['id'], rule_to_toggle['status'])
            except (ValueError, StopIteration): print_error("ID không hợp lệ.")
        elif choice == '3':
            try:
                rule_id_str = input("Nhập ID của rule cần xóa: ").strip()
                rule_to_delete = next(r for r in rules if r['id'] == rule_id_str)
                if input(f"Bạn có chắc muốn xóa rule cho '{rule_to_delete['url']}'? (y/n): ").lower() == 'y':
                    web_filter.delete_rule(ssh, rule_to_delete['id'])
            except (ValueError, StopIteration): print_error("ID không hợp lệ.")
        elif choice == '0':
            ssh.disconnect(); break
        input("\nNhấn Enter để tiếp tục...")
