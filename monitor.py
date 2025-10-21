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
    LOCAL_HOSTNAME = "Unknown_Server"
    LOCAL_IP = "127.0.0.1"

# --- Biến toàn cục để quản lý trạng thái ---
connection_is_up = True
downtime_start = None

# --- CÁC HÀM XỬ LÝ ---

def send_telegram_message(message):
    """Hàm đồng bộ để gọi hàm gửi tin nhắn bất đồng bộ."""
    try:
        asyncio.run(send_telegram_message_async(message))
    except Exception as e:
        print(f"❌ Lỗi khi chạy tác vụ gửi Telegram: {e}")

async def send_telegram_message_async(message):
    """Hàm bất đồng bộ thực sự thực hiện việc gửi tin nhắn."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Lỗi: Chưa cấu hình Telegram trong file .env")
        return
    
    # Luôn đính kèm tên của server gửi tin
    full_message = f"📡 *Gửi từ Server: `{LOCAL_HOSTNAME}`*\n\n{message}"
    
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=full_message, parse_mode=ParseMode.MARKDOWN)
        print(f"✅ Đã gửi thông báo Telegram thành công.")
    except Exception as e:
        print(f"❌ Lỗi khi gửi Telegram: {e}")

def run_diagnostics():
    """Chạy chẩn đoán nhanh và trả về kết quả."""
    print("🩺 Đang chạy chẩn đoán...")
    if not BRANCH_GATEWAY:
        return "Lỗi: `BRANCH_GATEWAY` chưa được cấu hình trong .env"

    # 1. Kiểm tra Gateway
    if os.system(f"ping -c 1 -W 2 {BRANCH_GATEWAY} > /dev/null 2>&1") != 0:
        return f"❌ *Sự cố Mạng Nội bộ*: Không thể ping đến gateway ({BRANCH_GATEWAY})."

    # 2. Kiểm tra Internet
    if os.system(f"ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1") != 0:
        return f"❌ *Sự cố Internet*: Có thể ping gateway, nhưng không thể ra Internet."
    
    return f"✅ *Mạng Nội bộ & Internet ổn định*: Vấn đề có thể do đường truyền VPN hoặc từ chi nhánh còn lại."

def heartbeat_server(host='0.0.0.0', port=HEARTBEAT_PORT):
    """Chạy listener ở chế độ nền để trả lời 'PONG'."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        while True:
            conn, _ = s.accept()
            with conn:
                if conn.recv(1024) == b'PING':
                    conn.sendall(b'PONG')

def monitor_connection():
    """Vòng lặp chính giám sát kết nối, chẩn đoán và gửi cảnh báo."""
    global connection_is_up, downtime_start
    other_branch = "HCM" if BRANCH_ID == "HN" else "HN"
    
    print(f"ℹ️ [{BRANCH_ID}] Bắt đầu giám sát kết nối đến {other_branch} ({REMOTE_HOST})...")

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((REMOTE_HOST, HEARTBEAT_PORT))
                s.sendall(b'PING')
                data = s.recv(1024)
                
                if data == b'PONG':
                    if not connection_is_up:
                        # --- KẾT NỐI VỪA ĐƯỢC KHÔI PHỤC ---
                        connection_is_up = True
                        now = datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh"))
                        downtime_str = str(now - downtime_start).split('.')[0] if downtime_start else "không xác định"
                        print(f"✅ [{now.strftime('%H:%M:%S')}] Kết nối đã được khôi phục.")
                        
                        # LOGIC PHÂN XỬ: Chỉ server có IP "nhỏ hơn" mới gửi tin khôi phục
                        if LOCAL_IP < REMOTE_HOST:
                            print(f"ℹ️ Tôi là server chính ({LOCAL_IP}), đang gửi thông báo khôi phục.")
                            message = (
                                f"✅ *KHÔI PHỤC KẾT NỐI {BRANCH_ID}-{other_branch}*\n\n"
                                f"Kết nối đã được thiết lập lại thành công.\n"
                                f"*Tổng thời gian gián đoạn:* `{downtime_str}`"
                            )
                            send_telegram_message(message)
                        else:
                            print(f"ℹ️ Tôi là server phụ ({LOCAL_IP}), sẽ không gửi thông báo khôi phục.")
                        
                        downtime_start = None
                    else:
                        print(f"✅ Kết nối ổn định.")
                    time.sleep(HEARTBEAT_INTERVAL)
                else:
                    raise ConnectionError("Phản hồi không hợp lệ từ server.")

        except Exception as e:
            if connection_is_up:
                # --- KẾT NỐI VỪA BỊ MẤT ---
                connection_is_up = False
                downtime_start = datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh"))
                print(f"🚨 [{downtime_start.strftime('%H:%M:%S')}] Mất kết nối! Lỗi: {e}")
                
                diagnostic_result = run_diagnostics()
                message = (
                    f"🚨 *CẢNH BÁO MẤT KẾT NỐI {BRANCH_ID}-{other_branch}*\n\n"
                    f"*Thời gian:* `{downtime_start.strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
                    f"*Kết quả chẩn đoán:*\n{diagnostic_result}"
                )
                send_telegram_message(message)
            else:
                print(f"🚨 Vẫn đang mất kết nối...")
            
            time.sleep(RECONNECT_INTERVAL)

# --- KHỐI LỆNH CHÍNH ĐỂ CHẠY ---
if __name__ == "__main__":
    if not all([BRANCH_ID, REMOTE_HOST, BRANCH_GATEWAY]):
        print("Lỗi: Vui lòng đặt đủ các biến BRANCH_ID, REMOTE_HOST, BRANCH_GATEWAY trong file .env")
    else:
        # Tất cả server đều chạy listener ở chế độ nền
        print(f"ℹ️ [{BRANCH_ID}] Khởi động heartbeat server listener...")
        server_thread = threading.Thread(target=heartbeat_server, daemon=True)
        server_thread.start()

        # Và tất cả server cũng đều chạy client để giám sát
        monitor_connection()
