# monitor.py
import socket
import time
import os
import threading
import telegram
import asyncio
from telegram.constants import ParseMode
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# --- Tải cấu hình từ file .env ---
load_dotenv()
BRANCH_ID = os.getenv("BRANCH_ID", "").upper()
REMOTE_HOST = os.getenv("REMOTE_HOST")
BRANCH_GATEWAY = os.getenv("BRANCH_GATEWAY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
HEARTBEAT_PORT = 9999
HEARTBEAT_INTERVAL = 15
RECONNECT_INTERVAL = 5

# --- Lấy thông tin của server hiện tại ---
try:
    LOCAL_HOSTNAME = socket.gethostname()
    LOCAL_IP = socket.gethostbyname(LOCAL_HOSTNAME)
except socket.gaierror:
    LOCAL_HOSTNAME = "Unknown_Server"; LOCAL_IP = "127.0.0.1"

# --- Quản lý trạng thái bằng file ---
STATE_FILE = ".downtime.log"

def get_initial_state():
    """Đọc file trạng thái để biết trạng thái ban đầu."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                timestamp_str = f.read().strip()
                downtime_start = datetime.fromisoformat(timestamp_str)
                return False, downtime_start # Trạng thái DOWN, có thời gian bắt đầu
        except Exception:
            return False, datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh")) # Lỗi đọc file, coi như DOWN từ bây giờ
    return True, None # Trạng thái UP, không có thời gian bắt đầu

# --- CÁC HÀM XỬ LÝ ---
def send_telegram_message(message):
    """Hàm wrapper để gửi tin nhắn Telegram."""
    try: asyncio.run(send_telegram_message_async(message))
    except Exception as e: print(f"❌ Lỗi khi chạy tác vụ gửi Telegram: {e}")

async def send_telegram_message_async(message):
    """Hàm async để gửi tin nhắn Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return
    full_message = f"📡 *Gửi từ Server: `{LOCAL_HOSTNAME}`*\n\n{message}"
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=full_message, parse_mode=ParseMode.MARKDOWN)
        print(f"✅ Đã gửi thông báo Telegram thành công.")
    except Exception as e: print(f"❌ Lỗi khi gửi Telegram: {e}")

def run_diagnostics():
    """Chạy chẩn đoán nhanh và trả về kết quả."""
    print("🩺 Đang chạy chẩn đoán...")
    if not BRANCH_GATEWAY: return "Lỗi: `BRANCH_GATEWAY` chưa được cấu hình."
    if os.system(f"ping -c 1 -W 2 {BRANCH_GATEWAY} > /dev/null 2>&1") != 0:
        return f"❌ *Sự cố Mạng Nội bộ*: Không thể ping đến gateway ({BRANCH_GATEWAY})."
    if os.system(f"ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1") != 0:
        return f"❌ *Sự cố Internet*: Có thể ping gateway, nhưng không thể ra Internet."
    return f"✅ *Mạng Nội bộ & Internet ổn định*: Vấn đề có thể do VPN hoặc từ chi nhánh còn lại."

def heartbeat_server(host='0.0.0.0', port=HEARTBEAT_PORT):
    """Chạy listener nền để trả lời 'PONG'."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind((host, port)); s.listen()
        while True:
            conn, _ = s.accept()
            with conn:
                if conn.recv(1024) == b'PING': conn.sendall(b'PONG')

def monitor_connection():
    """Vòng lặp chính giám sát kết nối."""
    connection_is_up, downtime_start = get_initial_state()
    other_branch = "HCM" if BRANCH_ID == "HN" else "HN"
    print(f"ℹ️ [{BRANCH_ID}] Bắt đầu giám sát {other_branch} ({REMOTE_HOST}). Trạng thái ban đầu: {'UP' if connection_is_up else 'DOWN'}")

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5); s.connect((REMOTE_HOST, HEARTBEAT_PORT)); s.sendall(b'PING'); data = s.recv(1024)
                if data == b'PONG':
                    if not connection_is_up:
                        connection_is_up = True
                        now = datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh"))
                        downtime_str = str(now - downtime_start).split('.')[0] if downtime_start else "không xác định"
                        print(f"✅ [{now.strftime('%H:%M:%S')}] Kết nối đã được khôi phục.")
                        if os.path.exists(STATE_FILE): os.remove(STATE_FILE)
                        
                       # if LOCAL_IP < REMOTE_HOST:
                        message = (f"✅ *KHÔI PHỤC KẾT NỐI {BRANCH_ID}-{other_branch}*\n\n"
                                   f"Kết nối đã được thiết lập lại thành công.\n"
                                   f"*Tổng thời gian gián đoạn:* `{downtime_str}`")
                        send_telegram_message(message)
                        
                        downtime_start = None
                    else:
                        print(f"✅ Kết nối ổn định.")
                    time.sleep(HEARTBEAT_INTERVAL)
                else:
                    raise ConnectionError("Phản hồi không hợp lệ.")
        except Exception as e:
            if connection_is_up:
                connection_is_up = False
                downtime_start = datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh"))
                with open(STATE_FILE, "w") as f: f.write(downtime_start.isoformat())
                print(f"🚨 [{downtime_start.strftime('%H:%M:%S')}] Mất kết nối! Lỗi: {e}")
                
                diagnostic_result = run_diagnostics()
                message = (f"🚨 *CẢNH BÁO MẤT KẾT NỐI {BRANCH_ID}-{other_branch}*\n\n"
                           f"*Thời gian:* `{downtime_start.strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
                           f"*Kết quả chẩn đoán:*\n{diagnostic_result}")
                send_telegram_message(message)
            else:
                print(f"🚨 Vẫn đang mất kết nối...")
            time.sleep(RECONNECT_INTERVAL)

if __name__ == "__main__":
    if not all([BRANCH_ID, REMOTE_HOST, BRANCH_GATEWAY]):
        print("Lỗi: Vui lòng đặt đủ các biến BRANCH_ID, REMOTE_HOST, BRANCH_GATEWAY trong file .env")
    else:
        server_thread = threading.Thread(target=heartbeat_server, daemon=True); server_thread.start()
        monitor_connection()
