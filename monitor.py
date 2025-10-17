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


def heartbeat_server(host='0.0.0.0', port=HEARTBEAT_PORT):
    """
    Chạy listener ở chế độ nền, lắng nghe 'PING' và trả lời 'PONG'.
    Hàm này sẽ chạy trên server HN.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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
    Client kết nối đến server kia để kiểm tra heartbeat.
    Hàm này sẽ chạy trên cả hai server.
    """
    global connection_is_up, downtime_start
    
    # Xác định vai trò dựa trên BRANCH_ID
    current_branch = get_current_branch()
    
    # Xác định IP của server đối phương
    # (Đây là giả định, bạn có thể thay bằng IP thật hoặc tên miền)
    other_server_ip = "10.20.3.10" if current_branch == "HN" else "10.10.4.10"
    
    print(f"ℹ️ [{current_branch}] Bắt đầu giám sát kết nối đến server {other_server_ip}...")

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5) # Chờ tối đa 5 giây
                s.connect((other_server_ip, HEARTBEAT_PORT))
                s.sendall(b'PING')
                data = s.recv(1024)
                if data == b'PONG':
                    if not connection_is_up:
                        # --- KẾT NỐI VỪA ĐƯỢC KHÔI PHỤC ---
                        connection_is_up = True
                        hcm_tz = ZoneInfo("Asia/Ho_Chi_Minh")
                        now = datetime.now(tz=hcm_tz)
                        print(f"✅ [{now.strftime('%H:%M:%S')}] Kết nối đã được khôi phục.")
                        # TODO: Gửi thông báo khôi phục qua Telegram
                    else:
                        print(f"✅ Kết nối ổn định.")

                    time.sleep(HEARTBEAT_INTERVAL)
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            if connection_is_up:
                # --- KẾT NỐI VỪA BỊ MẤT ---
                connection_is_up = False
                hcm_tz = ZoneInfo("Asia/Ho_Chi_Minh")
                downtime_start = datetime.now(tz=hcm_tz)
                print(f"🚨 [{downtime_start.strftime('%H:%M:%S')}] Mất kết nối! Lỗi: {e}")
                # TODO: Kích hoạt chẩn đoán và gửi cảnh báo Telegram
            else:
                print(f"🚨 Vẫn đang mất kết nối...")
            
            time.sleep(RECONNECT_INTERVAL)


if __name__ == "__main__":
    current_branch = get_current_branch()
    if not current_branch:
        print("Lỗi: Vui lòng đặt BRANCH_ID='HN' hoặc 'HCM' trong file .env")
    else:
        if current_branch == "HN":
            # Server HN sẽ chạy listener ở chế độ nền
            print("ℹ️ [HN] Khởi động heartbeat server listener...")
            server_thread = threading.Thread(target=heartbeat_server, daemon=True)
            server_thread.start()

        # Cả hai server đều chạy client để giám sát
        monitor_connection()
