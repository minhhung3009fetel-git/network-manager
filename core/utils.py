# core/utils.py
import os
import platform
import socket
from dotenv import load_dotenv

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

def load_credentials():
    """
    Tải username và password từ file .env.
    Trả về (username, password) nếu có, ngược lại trả về (None, None).
    """
    load_dotenv()  # Tải các biến môi trường từ file .env
    username = os.getenv("SSH_USERNAME")
    password = os.getenv("SSH_PASSWORD")
    return username, password

def get_current_branch():
    """Đọc mã chi nhánh (ví dụ: 'HN' hoặc 'HCM') từ file .env."""
    load_dotenv()
    # Mặc định là chuỗi rỗng nếu không được định nghĩa
    return os.getenv("BRANCH_ID", "").upper()
