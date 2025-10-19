# modules/bulk_config.py
import os
import yaml
import threading
from jinja2 import Template

from core.devices import load_devices
from core.utils import load_credentials, clear_screen
from core.ui import console, print_info, print_success, print_error, print_warning
from core.ssh_client import SSHClient

TEMPLATE_DIR = "core/templates"

def _load_templates():
    """Tải tất cả các mẫu cấu hình từ thư mục templates."""
    templates = []
    if not os.path.exists(TEMPLATE_DIR):
        return templates
    for filename in os.listdir(TEMPLATE_DIR):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            with open(os.path.join(TEMPLATE_DIR, filename), 'r', encoding='utf-8') as f:
                try:
                    templates.append(yaml.safe_load(f))
                except yaml.YAMLError as e:
                    print_error(f"Lỗi đọc file template {filename}: {e}")
    return templates

def _push_config_to_device(device, username, password, commands, results):
    """Hàm chạy trong thread, đẩy config tới 1 thiết bị."""
    device_name = device['name']
    try:
        ssh = SSHClient(device, username, password)
        if not ssh.connect():
            results[device_name] = (False, f"Không thể kết nối")
            return

        conn = ssh.conn
        output = conn.send_config_set(commands)
        results[device_name] = (True, output)
        ssh.disconnect()
    except Exception as e:
        results[device_name] = (False, str(e))

def run_bulk_config_push():
    """Hàm chính điều phối chức năng đẩy cấu hình hàng loạt."""
    clear_screen()
    console.rule("[bold yellow]🚀 Đẩy Cấu hình Hàng loạt[/bold yellow]")

    # 1. Chọn Template
    templates = _load_templates()
    if not templates:
        print_error("Không tìm thấy mẫu cấu hình nào trong thư mục core/templates/"); return
    
    print_info("Các mẫu cấu hình có sẵn:")
    for i, t in enumerate(templates, 1):
        print(f" [{i}] {t['name']} - {t['description']}")
    print("\n [0] Quay lại")

    try:
        choice = int(input("\nChọn mẫu để đẩy: ").strip())
        if choice == 0: print_info("Đã hủy."); return
        selected_template = templates[choice - 1]
    except (ValueError, IndexError):
        print_error("Lựa chọn không hợp lệ."); return

    # 2. Nhập các biến
    variables = {}
    if 'variables' in selected_template:
        for var in selected_template['variables']:
            val = input(f"> {var['prompt']} [mặc định: {var['default']}]: ").strip()
            variables[var['name']] = val if val else var['default']

    # 3. Chọn thiết bị
    devices = load_devices()
    device_list = list(devices.items())
    print_info("\nChọn các thiết bị để áp dụng cấu hình:")
    for i, (name, info) in enumerate(device_list, 1):
        print(f" [{i}] {name} ({info['device_type']})")
    
    target_input = input("\nNhập số thứ tự (ví dụ: 1,3,5) hoặc 'all' để chọn tất cả: ").strip().lower()

    if not target_input:
        print_info("Đã hủy."); return
    
    target_devices = []
    if target_input == 'all':
        target_devices = [{'name': name, **info} for name, info in device_list]
    else:
        try:
            indices = [int(i.strip()) - 1 for i in target_input.split(',')]
            for i in indices:
                name, info = device_list[i]
                target_devices.append({'name': name, **info})
        except (ValueError, IndexError):
            print_error("Định dạng lựa chọn không hợp lệ."); return

    # 4. Xác nhận và thực thi
    print_warning(f"\nBạn sắp đẩy mẫu '{selected_template['name']}' lên {len(target_devices)} thiết bị.")
    if input("Bạn có chắc chắn muốn tiếp tục? (y/n): ").lower() != 'y':
        print_info("Đã hủy."); return

    username, password = load_credentials()
    if not (username and password):
        print_error("Không thể tải thông tin đăng nhập từ file .env."); return

    threads = []
    results = {}
    print_info("\nBắt đầu đẩy cấu hình...")
    for device in target_devices:
        device_type = device['device_type']
        if device_type in selected_template['commands']:
            template = Template("\n".join(selected_template['commands'][device_type]))
            rendered_commands = template.render(variables).splitlines()
            
            thread = threading.Thread(
                target=_push_config_to_device,
                args=(device, username, password, rendered_commands, results)
            )
            threads.append(thread)
            thread.start()
        else:
            results[device['name']] = (False, f"Không có mẫu cho loại '{device_type}'")

    for thread in threads:
        thread.join()

    # 5. Báo cáo kết quả
    console.rule("[bold green]Kết quả Đẩy Cấu hình[/bold green]")
    for name, (success, output) in results.items():
        if success:
            print_success(f"✅ {name}: Thành công")
        else:
            print_error(f"❌ {name}: Thất bại - {output}")
