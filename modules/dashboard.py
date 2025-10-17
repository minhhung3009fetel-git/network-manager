# modules/dashboard.py
import time
import sys
import select
from datetime import datetime
from zoneinfo import ZoneInfo
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns

from modules.connection_check import get_all_device_statuses

REFRESH_INTERVAL = 60 # Giây

def user_pressed_enter():
    """Kiểm tra xem người dùng có nhấn Enter không mà không chặn chương trình."""
    # select.select sẽ kiểm tra stdin (đầu vào chuẩn)
    # Timeout = 0 có nghĩa là nó không chờ đợi, chỉ kiểm tra ngay lập tức
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def generate_layout(dashboard_data, time_left, is_refreshing):
    """Tạo và trả về đối tượng Layout cho dashboard."""
    # --- Định nghĩa cấu trúc layout ---
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(ratio=1, name="main_body"),
    )
    layout["main_body"].split(Layout(name="top"), Layout(name="alert", visible=False))
    layout["top"].split_row(Layout(name="summary"), Layout(name="menu"))

    # --- Phần Header (Tiêu đề và Đồng hồ) ---
    hcm_tz = ZoneInfo("Asia/Ho_Chi_Minh")
    current_time = datetime.now(tz=hcm_tz).strftime("%Y-%m-%d %H:%M:%S")
    header_text = Text("🚀 NETWORK DEVICE MANAGER 🚀", style="bold yellow", justify="center")
    time_text = Text(f"Server Time: {current_time}", justify="right")
    
    header_columns = Columns([header_text, time_text])
    layout["header"].update(Panel(header_columns, style="bold cyan", border_style="cyan"))

    # --- Phần Thân (Tóm tắt & Menu) ---
    total_devices = len(dashboard_data)
    down_devices = [res for res in dashboard_data if res[2] != "UP"]
    up_count = total_devices - len(down_devices)
    down_count = len(down_devices)

    # Panel Tóm tắt
    countdown_str = f"🔄 Đang làm mới..." if is_refreshing else f"Cập nhật sau {int(time_left)}s"
    summary_text = Text()
    summary_text.append("  - Tổng số thiết bị: ", style="default")
    summary_text.append(f"{total_devices}\n", style="bold")
    summary_text.append("  - Đang hoạt động:   ", style="default")
    summary_text.append(f"{up_count}\n", style="bold green")
    summary_text.append("  - Gặp sự cố:        ", style="default")
    summary_text.append(f"{down_count}", style="bold red")
    summary_panel = Panel(summary_text, title=f"📊 TỔNG QUAN - {countdown_str}", border_style="cyan")

    # Panel Menu
    menu_text = "[1] Quản lý thiết bị\n[2] Thao tác với thiết bị\n[3] In lại bảng trạng thái\n[R] Làm mới Dashboard\n[0] Thoát\n\n[bold]Nhấn [ENTER] để vào Menu[/bold]"
    menu_panel = Panel(menu_text, title="🛠️ MENU", border_style="green")

    layout["summary"].update(summary_panel)
    layout["menu"].update(menu_panel)

    # --- Phần Cảnh báo (Chỉ hiện khi có sự cố) ---
    if down_count > 0:
        layout["alert"].visible = True
        alert_text = Text("Các thiết bị sau đang gặp sự cố:\n", style="default")
        for name, ip, status in down_devices:
            style = "bold red" if status == "DOWN" else "bold yellow"
            alert_text.append(f"  - {name} ({ip})\n", style=style)
        layout["alert"].update(Panel(alert_text, title="⚠️ CẢNH BÁO", border_style="red"))

    return layout

def run_live_dashboard():
    """Chạy dashboard live-updating cho đến khi người dùng nhấn Enter."""
    last_update_time = 0
    dashboard_data = []
    is_refreshing = False

    with Live(generate_layout([], REFRESH_INTERVAL, True), screen=True, redirect_stderr=False, auto_refresh=False) as live:
        while True:
            # Kiểm tra nếu người dùng muốn vào menu
            if user_pressed_enter():
                # Xóa bộ đệm đầu vào để không ảnh hưởng đến lần input() tiếp theo
                sys.stdin.readline()
                break

            current_time = time.time()
            time_since_last_update = current_time - last_update_time
            
            # Logic làm mới dữ liệu
            if time_since_last_update >= REFRESH_INTERVAL and not is_refreshing:
                is_refreshing = True
                live.update(generate_layout(dashboard_data, 0, is_refreshing), refresh=True)
                dashboard_data = get_all_device_statuses()
                last_update_time = time.time()
                is_refreshing = False

            time_left = REFRESH_INTERVAL - (time.time() - last_update_time)
            live.update(generate_layout(dashboard_data, time_left, is_refreshing), refresh=True)
            time.sleep(1)
