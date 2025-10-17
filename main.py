# main.py
from core.devices import list_devices, add_device, delete_device
from core.ui import console, print_error, print_success, print_warning
from core.utils import clear_screen
from core.backup_restore import backup_all_devices
from modules.connection_check import check_all_devices_concurrently
from modules.dashboard import run_live_dashboard # <-- Import màn hình live
from main_actions import select_device_and_run_actions, menu_device_manager, menu_restore

def main_menu():
    """Vòng lặp menu chính sau khi dashboard đã thoát."""
    while True:
        clear_screen()
        print("\n" * 2) # Tạo khoảng trống
        console.rule("[bold yellow]MENU CHÍNH[/bold yellow]")
        print(" [1] Quản lý danh sách thiết bị")
        print(" [2] Kết nối và thao tác với thiết bị")
        print(" [3] In lại bảng trạng thái chi tiết")
        print(" [4] Backup toàn bộ hệ thống")
        print(" [5] Khôi phục cấu hình (Restore)")
        print(" [R] Hiển thị lại Dashboard")
        print(" [0] Thoát chương trình")
        
        choice = input("\nChọn chức năng: ").strip().lower()

        if choice == '1':
            menu_device_manager()
        elif choice == '2':
            select_device_and_run_actions()
        elif choice == '3':
            check_all_devices_concurrently()
            input("\nNhấn Enter để tiếp tục...")
        elif choice == '4':
            backup_all_devices()
        elif choice == '5':
            menu_restore()
        elif choice == 'r':
            run_live_dashboard() # Gọi lại dashboard
        elif choice == '0':
            clear_screen()
            console.print("[bold blue]👋 Tạm biệt![/bold blue]")
            break
        else:
            print_error("Lựa chọn không hợp lệ.")
            input("\nNhấn Enter để tiếp tục...")


if __name__ == "__main__":
    # Chạy màn hình live dashboard trước
    run_live_dashboard()
    
    # Sau khi người dùng nhấn Enter, vào menu chính
    main_menu()
