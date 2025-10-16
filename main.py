# main.py
import getpass
from modules.interface_info import show_interface_info
from modules.system_health import show_system_health
from modules.connection_check import check_all_devices_concurrently
from core.backup_restore import backup_device_config
from core.utils import clear_screen, is_device_reachable, load_credentials
from core.devices import list_devices, add_device, load_devices, delete_device
from core.ui import console, print_panel, print_error, print_success, print_info, print_warning

def menu_device_manager():
    """Menu con để quản lý danh sách thiết bị."""
    while True:
        clear_screen()
        menu_text = "[1] Xem danh sách thiết bị\n[2] Thêm thiết bị mới\n[3] Xóa thiết bị\n[0] Quay lại menu chính"
        print_panel(menu_text, title="🔧 QUẢN LÝ THIẾT BỊ")
        choice = input("Chọn: ").strip()

        if choice == "1":
            list_devices()
            input("\nNhấn Enter để tiếp tục...")
        elif choice == "2":
            add_device()
            input("\nNhấn Enter để tiếp tục...")
        elif choice == "3":
            delete_device()
            input("\nNhấn Enter để tiếp tục...")
        elif choice == "0":
            break
        else:
            print_error("Lựa chọn không hợp lệ, vui lòng chọn lại.")
            input("\nNhấn Enter để tiếp tục...")

def menu_device_actions(device, username, password):
    """Menu con để thực hiện các tác vụ trên thiết bị đã chọn."""
    while True:
        clear_screen()
        console.rule(f"Đang thao tác trên: [bold cyan]{device['name']} ({device['ip']})[/bold cyan]")
        menu_text = "[1] Xem thông tin Interface\n[2] Kiểm tra tình trạng hệ thống\n[3] Backup cấu hình\n[0] Quay lại"
        print_panel(menu_text, title="🛠️ CHỌN TÁC VỤ")
        choice = input("Chọn tác vụ: ").strip()

        if choice == "1":
            show_interface_info(device, username, password)
            input("\nNhấn Enter để tiếp tục...")
        elif choice == "2":
            show_system_health(device, username, password)
            input("\nNhấn Enter để tiếp tục...")
        elif choice == "3":
            backup_device_config(device, username, password)
            input("\nNhấn Enter để tiếp tục...")
        elif choice == "0":
            break
        else:
            print_error("Lựa chọn không hợp lệ, vui lòng chọn lại.")
            input("\nNhấn Enter để tiếp tục...")

def select_device_and_run_actions():
    """Hiển thị danh sách thiết bị và cho phép người dùng chọn một để thao tác."""
    clear_screen()
    devices = load_devices()
    if not devices:
        print_warning("Chưa có thiết bị nào trong danh sách. Vui lòng thêm thiết bị trước.")
        input("\nNhấn Enter để tiếp tục...")
        return

    device_list = [{'name': name, **info} for name, info in devices.items()]

    console.rule("[bold yellow]CHỌN THIẾT BỊ ĐỂ KẾT NỐI[/bold yellow]")
    for i, device in enumerate(device_list, start=1):
        console.print(f"  [cyan]{i})[/cyan] {device['name']} ({device['ip']})")
    console.print("  [cyan]0)[/cyan] Quay lại menu chính")

    try:
        choice = int(input("\nChọn thiết bị: ").strip())
        if choice == 0:
            return
        if 0 < choice <= len(device_list):
            selected_device = device_list[choice - 1]
            print_info(f"Đang kiểm tra kết nối đến {selected_device['name']} ({selected_device['ip']})...")

            if is_device_reachable(selected_device['ip']):
                print_success("Thiết bị đang hoạt động!")
                # --- LOGIC MỚI ĐỂ ĐĂNG NHẬP ---
                username, password = load_credentials() # Thử tải tự động

                if username and password:
                    print_info(f"Sử dụng thông tin đăng nhập tự động từ file .env (user: {username})")
                else:
                    # Nếu không có, hỏi thủ công
                    print_warning("Không tìm thấy file .env. Vui lòng nhập thông tin đăng nhập.")
                    username = input("Nhập SSH username: ").strip()
                    password = getpass.getpass("Nhập SSH password: ").strip()
                # --- KẾT THÚC LOGIC MỚI ---

                # Truyền thông tin đăng nhập vào menu tác vụ
                menu_device_actions(selected_device, username, password)
            else:
                print_error(f"Không thể kết nối đến thiết bị {selected_device['name']}. Vui lòng kiểm tra lại.")
                input("\nNhấn Enter để tiếp tục...")
        else:
            print_error("Lựa chọn không hợp lệ.")
            input("\nNhấn Enter để tiếp tục...")
    except ValueError:
        print_error("Vui lòng nhập một số.")
        input("\nNhấn Enter để tiếp tục...")

def main():
    """Hàm main, menu chính của chương trình."""
    while True:
        clear_screen()
        menu_text = "[1] Quản lý danh sách thiết bị\n[2] Kết nối và thao tác với thiết bị\n[3] Kiểm tra trạng thái tất cả thiết bị\n[0] Thoát chương trình"
        print_panel(menu_text, title="🚀 NETWORK DEVICE MANAGER 🚀", style="bold yellow")
        choice = input("Chọn chức năng: ").strip()

        if choice == "1":
            menu_device_manager()
        elif choice == "2":
            select_device_and_run_actions()
        elif choice == "3":
            check_all_devices_concurrently()
            input("\nNhấn Enter để tiếp tục...")
        elif choice == "0":
            clear_screen()
            console.print("[bold blue]👋 Tạm biệt![/bold blue]")
            break
        else:
            print_error("Lựa chọn không hợp lệ, vui lòng chọn lại.")
            input("\nNhấn Enter để tiếp tục...")

if __name__ == "__main__":
    main()
