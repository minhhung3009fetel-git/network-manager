# main_actions.py
import getpass
from core.devices import list_devices, add_device, delete_device, load_devices
from core.ui import console, print_panel, print_error, print_success, print_info, print_warning
from core.utils import clear_screen, is_device_reachable, load_credentials
from core.backup_restore import backup_device_config
from modules.interface_info import show_interface_info
from modules.system_health import show_system_health

def menu_device_manager():
    # ... (Copy y hệt hàm menu_device_manager từ file main.py cũ của bạn vào đây) ...
    while True:
        clear_screen()
        menu_text = "[1] Xem danh sách\n[2] Thêm thiết bị\n[3] Xóa thiết bị\n[0] Quay lại"
        print_panel(menu_text, title="🔧 QUẢN LÝ THIẾT BỊ")
        choice = input("Chọn: ").strip()
        if choice == "1": list_devices(); input("\nNhấn Enter...")
        elif choice == "2": add_device(); input("\nNhấn Enter...")
        elif choice == "3": delete_device(); input("\nNhấn Enter...")
        elif choice == "0": break
        else: print_error("Lựa chọn không hợp lệ."); input("\nNhấn Enter...")


def menu_device_actions(device, username, password):
    # ... (Copy y hệt hàm menu_device_actions từ file main.py cũ của bạn vào đây) ...
    while True:
        clear_screen()
        console.rule(f"Đang thao tác trên: [bold cyan]{device['name']} ({device['ip']})[/bold cyan]")
        menu_text = "[1] Xem thông tin Interface\n[2] Kiểm tra hệ thống\n[3] Backup cấu hình\n[0] Quay lại"
        print_panel(menu_text, title="🛠️ CHỌN TÁC VỤ")
        choice = input("Chọn: ").strip()
        if choice == "1": show_interface_info(device, username, password); input("\nNhấn Enter...")
        elif choice == "2": show_system_health(device, username, password); input("\nNhấn Enter...")
        elif choice == "3": backup_device_config(device, username, password); input("\nNhấn Enter...")
        elif choice == "0": break
        else: print_error("Lựa chọn không hợp lệ."); input("\nNhấn Enter...")


def select_device_and_run_actions():
    # ... (Copy y hệt hàm select_device_and_run_actions từ file main.py cũ của bạn vào đây) ...
    clear_screen()
    devices = load_devices()
    if not devices:
        print_warning("Chưa có thiết bị. Vui lòng thêm."); input("\nNhấn Enter..."); return

    device_list = [{'name': name, **info} for name, info in devices.items()]
    console.rule("[bold yellow]CHỌN THIẾT BỊ[/bold yellow]")
    for i, device in enumerate(device_list, start=1): console.print(f"  [cyan]{i})[/cyan] {device['name']} ({device['ip']})")
    console.print("  [cyan]0)[/cyan] Quay lại")
    try:
        choice = int(input("\nChọn: ").strip())
        if choice == 0: return
        if 0 < choice <= len(device_list):
            selected_device = device_list[choice - 1]
            if is_device_reachable(selected_device['ip']):
                print_success("Thiết bị đang hoạt động!")
                username, password = load_credentials()
                if not (username and password):
                    username = input("Username: ").strip()
                    password = getpass.getpass("Password: ").strip()
                menu_device_actions(selected_device, username, password)
            else: print_error(f"Không thể kết nối."); input("\nNhấn Enter...")
        else: print_error("Lựa chọn không hợp lệ."); input("\nNhấn Enter...")
    except ValueError: print_error("Vui lòng nhập số."); input("\nNhấn Enter...")
