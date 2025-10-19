# main.py
import time
from core.ui import print_error, console
from core.utils import clear_screen
from modules.dashboard import run_live_dashboard
from modules.connection_check import check_all_devices_concurrently
from modules.diagnostics import run_diagnostics
from modules.bulk_config import run_bulk_config_push
from core.backup_restore import backup_all_devices
from main_actions import (
    menu_device_manager, 
    menu_restore, 
    menu_interaction
)

def menu_monitoring_diagnostics():
    """Menu con cho Giám sát & Chẩn đoán."""
    while True:
        clear_screen()
        console.rule("[bold cyan]GIÁM SÁT & CHẨN ĐOÁN[/bold cyan]")
        print(" [1] Hiển thị lại Dashboard Live")
        print(" [2] In bảng trạng thái chi tiết")
        print(" [3] Chẩn đoán sự cố thiết bị")
        print("\n [0] Quay lại")
        choice = input("\nChọn chức năng: ").strip().lower()

        if choice == '1':
            run_live_dashboard()
        elif choice == '2':
            check_all_devices_concurrently()
            input("\nNhấn Enter để tiếp tục...")
        elif choice == '3':
            run_diagnostics()
            input("\nNhấn Enter để tiếp tục...")
        elif choice == '0':
            break
        else:
            print_error("Lựa chọn không hợp lệ.")
            time.sleep(1)

def menu_config_management():
    """Menu con cho Quản lý Cấu hình."""
    while True:
        clear_screen()
        console.rule("[bold green]QUẢN LÝ CẤU HÌNH[/bold green]")
        print(" [1] Backup toàn bộ hệ thống")
        print(" [2] Khôi phục cấu hình (Restore)")
        print(" [3] Đẩy cấu hình hàng loạt")
        print("\n [0] Quay lại")
        choice = input("\nChọn chức năng: ").strip().lower()

        if choice == '1':
            backup_all_devices()
            input("\nNhấn Enter để tiếp tục...")
        elif choice == '2':
            menu_restore()
        elif choice == '3':
            run_bulk_config_push()
            input("\nNhấn Enter để tiếp tục...")
        elif choice == '0':
            break
        else:
            print_error("Lựa chọn không hợp lệ.")
            time.sleep(1)

def main_menu():
    """Hàm hiển thị menu chính đã được tái cấu trúc."""
    while True:
        clear_screen()
        console.print("\n" * 2)
        console.rule("[bold yellow]MENU CHÍNH[/bold yellow]")
        print(" [1] Giám sát & Chẩn đoán")
        print(" [2] Quản lý Cấu hình")
        print(" [3] Tương tác Trực tiếp")
        print(" [4] Quản lý Danh sách Thiết bị")
        print("\n [0] Thoát chương trình")
        
        choice = input("\nChọn chức năng: ").strip().lower()
        
        if choice == '1':
            menu_monitoring_diagnostics()
        elif choice == '2':
            menu_config_management()
        elif choice == '3':
            menu_interaction()
        elif choice == '4':
            menu_device_manager()
        elif choice == '0':
            clear_screen(); console.print("[bold blue]👋 Tạm biệt![/bold blue]"); break
        else:
            print_error("Lựa chọn không hợp lệ.")
            time.sleep(1)

if __name__ == "__main__":
    # Chạy màn hình live dashboard trước khi vào menu chính
    run_live_dashboard()
    main_menu()
