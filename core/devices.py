# core/devices.py
import os
from core.ui import console, create_table, print_success, print_warning, print_error

DATA_FILE = "data/devices.txt"

def ensure_data_file():
    """Tạo thư mục và file nếu chưa có"""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        open(DATA_FILE, "w").close()

def load_devices():
    """Đọc danh sách thiết bị"""
    ensure_data_file()
    devices = {}
    with open(DATA_FILE, "r") as f:
        for line in f:
            if line.strip():
                try:
                    name, ip, dtype = line.strip().split(",")
                    devices[name] = {"ip": ip, "device_type": dtype}
                except ValueError:
                    print_warning(f"⚠️ Bỏ qua dòng lỗi: {line.strip()}")
    return devices

def save_devices(devices):
    """Ghi lại danh sách thiết bị"""
    ensure_data_file()
    with open(DATA_FILE, "w") as f:
        for name, info in devices.items():
            f.write(f"{name},{info['ip']},{info['device_type']}\n")

def add_device():
    """Thêm thiết bị mới"""
    ensure_data_file()
    console.rule("[bold green]Thêm thiết bị mới[/bold green]")
    name = input("Tên thiết bị: ").strip()
    ip = input("Địa chỉ IP: ").strip()
    dtype = input("Loại thiết bị (vd: cisco_ios, fortinet, mikrotik): ").strip()

    devices = load_devices()
    if name in devices:
        print_warning("⚠️ Thiết bị này đã tồn tại!")
        return

    devices[name] = {"ip": ip, "device_type": dtype}
    save_devices(devices)
    print_success(f"✅ Đã thêm thiết bị {name} ({ip})")

def list_devices():
    """Hiển thị danh sách thiết bị"""
    devices = load_devices()
    if not devices:
        print_warning("❌ Chưa có thiết bị nào.")
        return
    table = create_table(
        "DANH SÁCH THIẾT BỊ",
        {"STT": "dim", "Tên thiết bị": "cyan", "Địa chỉ IP": "green", "Loại thiết bị": "yellow"}
    )

    for i, (name, info) in enumerate(devices.items(), start=1):
        table.add_row(str(i), name, info['ip'], info['device_type'])

    console.print(table)

def delete_device():
    """Hiển thị danh sách và xóa một thiết bị được chọn."""
    devices = load_devices()
    if not devices:
        print_warning("Không có thiết bị nào để xóa.")
        return

    console.rule("[bold red]Xóa một thiết bị[/bold red]")
    device_names = list(devices.keys())

    # Hiển thị danh sách thiết bị để người dùng chọn
    for i, name in enumerate(device_names, start=1):
        console.print(f"  [cyan]{i})[/cyan] {name} ({devices[name]['ip']})")

    try:
        choice = int(input("\nChọn số thứ tự của thiết bị cần xóa (nhập 0 để hủy): ").strip())
        
        if choice == 0:
            print_info("Hủy bỏ thao tác xóa.")
            return

        if 0 < choice <= len(device_names):
            device_to_delete = device_names[choice - 1]

            # Thêm bước xác nhận để tránh xóa nhầm
            confirm = input(f"⚠️ Bạn có chắc chắn muốn xóa '{device_to_delete}' không? (y/n): ").strip().lower()

            if confirm == 'y':
                # Xóa thiết bị khỏi dictionary
                del devices[device_to_delete]
                # Lưu lại danh sách mới vào file
                save_devices(devices)
                print_success(f"Đã xóa thành công thiết bị '{device_to_delete}'.")
            else:
                print_info("Hủy bỏ thao tác xóa.")
        else:
            print_error("Lựa chọn không hợp lệ.")
    except ValueError:
        print_error("Vui lòng nhập một số hợp lệ.")
