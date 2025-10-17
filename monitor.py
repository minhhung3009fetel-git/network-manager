# monitor.py
import socket
import time
import os
import threading
import telegram
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from core.utils import get_current_branch, load_telegram_config

# --- Cấu hình ---
HEARTBEAT_PORT = 9999
HEARTBEAT_INTERVAL = 15 # Giây
RECONNECT_INTERVAL = 5  # Giây

# --- Biến toàn cục để quản lý trạng thái ---
connection_is_up = True
downtime_start = None

def send_telegram_message(message):
    """Hàm gửi tin nhắn qua Telegram."""
    token, chat_id = load_telegram_config()
    if not token or not chat_id:
        print("⚠️ Lỗi: Chưa cấu hình TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID trong file .env")
        return

    try:
        bot = telegram.Bot(token=token)
        bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
        print(f"✅ Đã gửi thông báo Telegram thành công.")
    except Exception as e:
        print(f"❌ Lỗi khi gửi Telegram: {e}")

def run_diagnostics():
    """
    Chạy chẩn đoán nhanh để xác định nguyên nhân sự cố.
    Trả về một chuỗi mô tả kết quả.
    """
    # --- THAY ĐỔI CÁC IP NÀY CHO ĐÚNG VỚI MẠNG CỦA BẠN ---
    current_branch = get_current_branch()
    gateway_ip = "10.10.0.1" if current_branch == "HN" else "10.20.0.1"
    internet_ip = "8.8.8.8"

    print("🩺 Đang chạy chẩn đoán...")
    
    # 1. Kiểm tra Gateway
    response = os.system(f"ping -c 1 -W 2 {gateway_ip} > /dev/null 2>&1")
    if response != 0:
        return f"❌ **Sự cố Mạng Nội bộ**: Không thể ping đến gateway ({gateway_ip})."

    # 2. Kiểm tra Internet
    response = os.system(f"ping -c 1 -W 2 {internet_ip} > /dev/null 2>&1")
    if response != 0:
        return f"❌ **Sự cố Mất Internet**: Không thể ping đến {internet_ip}."

    return f"✅ **Mạng Nội bộ & Internet ổn định**: Vấn đề có thể do đường truyền VPN hoặc từ chi nhánh còn lại."

def heartbeat_server(host='0.0.0.0', port=HEARTBEAT_PORT):
    """
    Chạy listener ở chế độ nền, lắng nghe 'PING' và trả lời 'PONG'.
    Hàm này sẽ chạy trên server HN.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                if data == b'PING':
                    conn.sendall(b'PONG')


def monitor_connection():
    """
    Client kết nối đến server kia để kiểm tra heartbeat, chẩn đoán và gửi cảnh báo.
    """
    global connection_is_up, downtime_start
    
    current_branch = get_current_branch()
    other_branch = "HCM" if current_branch == "HN" else "HN"
    other_server_ip = "10.20.3.10" if current_branch == "HN" else "10.10.4.10" # Sửa IP nếu cần
    
    print(f"ℹ️ [{current_branch}] Bắt đầu giám sát kết nối đến server {other_server_ip}...")

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((other_server_ip, HEARTBEAT_PORT))
                s.sendall(b'PING')
                data = s.recv(1024)
                if data == b'PONG':
                    if not connection_is_up:
                        # --- KẾT NỐI VỪA ĐƯỢC KHÔI PHỤC ---
                        connection_is_up = True
                        hcm_tz = ZoneInfo("Asia/Ho_Chi_Minh")
                        now = datetime.now(tz=hcm_tz)
                        
                        if downtime_start:
                            downtime_delta = now - downtime_start
                            downtime_str = str(downtime_delta).split('.')[0] # Bỏ microsecond
                        else:
                            downtime_str = "không xác định"

                        print(f"✅ [{now.strftime('%H:%M:%S')}] Kết nối đã được khôi phục.")
                        
                        message = (
                            f"✅ *KHÔI PHỤC KẾT NỐI {current_branch}-{other_branch}*\n\n"
                            f"Kết nối đã được thiết lập lại thành công.\n"
                            f"*Tổng thời gian gián đoạn:* `{downtime_str}`"
                        )
                        send_telegram_message(message)
                        downtime_start = None
                    else:
                        print(f"✅ Kết nối ổn định.")

                    time.sleep(HEARTBEAT_INTERVAL)
        except Exception as e:
            if connection_is_up:
                # --- KẾT NỐI VỪA BỊ MẤT ---
                connection_is_up = False
                hcm_tz = ZoneInfo("Asia/Ho_Chi_Minh")
                downtime_start = datetime.now(tz=hcm_tz)
                
                print(f"🚨 [{downtime_start.strftime('%H:%M:%S')}] Mất kết nối! Lỗi: {e}")
                
                # Chạy chẩn đoán
                diagnostic_result = run_diagnostics()
                
                # Gửi cảnh báo
                message = (
                    f"🚨 *CẢNH BÁO MẤT KẾT NỐI {current_branch}-{other_branch}*\n\n"
                    f"*Phát hiện tại:* Server `{current_branch}`\n"
                    f"*Thời gian:* `{downtime_start.strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
                    f"*Kết quả chẩn đoán:*\n{diagnostic_result}"
                )
                send_telegram_message(message)
            else:
                print(f"🚨 Vẫn đang mất kết nối...")
            
            time.sleep(RECONNECT_INTERVAL)


if __name__ == "__main__":
    current_branch = get_current_branch()
    if not current_branch:
        print("Lỗi: Vui lòng đặt BRANCH_ID='HN' hoặc 'HCM' trong file .env")
    else:
        # TẤT CẢ các server đều sẽ chạy listener ở chế độ nền
        print(f"ℹ️ [{current_branch}] Khởi động heartbeat server listener...")
        server_thread = threading.Thread(target=heartbeat_server, daemon=True)
        server_thread.start()

        # Và TẤT CẢ các server cũng đều chạy client để giám sát
        monitor_connection()
