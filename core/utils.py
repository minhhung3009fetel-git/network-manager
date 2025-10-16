# core/utils.py
import os
import platform
import socket

def clear_screen():
    """Xóa màn hình console, hoạt động trên cả Windows, macOS và Linux."""
    system_name = platform.system()
    if system_name == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def is_device_reachable(ip, port=22, timeout=3):
    """
    Kiểm tra kết nối TCP nhanh đến một IP và port.
    Trả về True nếu kết nối được, False nếu thất bại.
    """
    try:
        # Tạo một socket mới
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            # Thử kết nối, connect_ex trả về 0 nếu thành công
            if s.connect_ex((ip, port)) == 0:
                return True
    except (socket.gaierror, socket.error):
        # Bắt các lỗi liên quan đến DNS hoặc không thể tạo socket
        return False
    # Nếu có bất kỳ lỗi nào khác hoặc không thành công
    return False
