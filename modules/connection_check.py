# modules/connection_check.py
import socket
import threading
from core.devices import load_devices
from core.ui import console, create_table, print_warning, print_info

def check_device_status(device_name, device_ip, results):
    """
    Kiểm tra xem cổng 22 (SSH) của thiết bị có mở hay không.
    Đây là cách nhanh để xác định thiết bị có 'sống' trên mạng hay không.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3) # Timeout 3 giây cho mỗi lần kiểm tra
            # connect_ex trả về 0 nếu thành công
            if s.connect_ex((device_ip, 22)) == 0:
                results.append((device_name, device_ip, "UP"))
            else:
                results.append((device_name, device_ip, "DOWN"))
    except socket.gaierror:
        results.append((device_name, device_ip, "INVALID_IP"))
    except Exception:
        results.append((device_name, device_ip, "DOWN"))


def check_all_devices_concurrently():
    """
    Sử dụng đa luồng để kiểm tra kết nối đến tất cả thiết bị cùng lúc.
    """
    devices = load_devices()
    if not devices:
        print_warning("❌ Chưa có thiết bị nào trong danh sách.")
        return

    print_info("\n🔄 Đang kiểm tra kết nối đến tất cả thiết bị...")
    
    threads = []
    results = []
    
    for name, info in devices.items():
        thread = threading.Thread(target=check_device_status, args=(name, info['ip'], results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join() # Chờ tất cả các luồng hoàn thành

    # Sắp xếp kết quả để dễ nhìn
    results.sort()

    table = create_table(
        "KẾT QUẢ KIỂM TRA KẾT NỐI",
        {"Tên thiết bị": "cyan", "Địa chỉ IP": "green", "Trạng thái": "dim"}
    )

    for name, ip, status in results:
        status_style = ""
        if status == "UP":
            status_style = "[bold green]✅ UP[/bold green]"
        elif status == "DOWN":
            status_style = "[bold red]❌ DOWN[/bold red]"
        else:
            status_style = "[bold yellow]⚠️ INVALID IP[/bold yellow]"
        table.add_row(name, ip, status_style)

    console.print(table)
