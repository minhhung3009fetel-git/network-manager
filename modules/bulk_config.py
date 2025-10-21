# modules/bulk_config.py
import os
import yaml
import threading
from jinja2 import Template

from core.devices import load_devices
from core.utils import load_credentials, clear_screen
from core.ui import console, print_info, print_success, print_error, print_warning

TEMPLATE_DIR = "core/templates"

def _load_templates_from_path(path):
    """Tải tất cả các mẫu cấu hình từ một đường dẫn cụ thể."""
    templates = []
    if not os.path.exists(path): return templates
    for filename in sorted(os.listdir(path)):
        if filename.endswith((".yaml", ".yml")):
            filepath = os.path.join(path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    templates.append(yaml.safe_load(f))
                except yaml.YAMLError as e:
                    print_error(f"Lỗi đọc file {filename}: {e}")
    return templates

def _push_config_to_device(device, username, password, commands, results):
    """Hàm chạy trong thread, đẩy config tới 1 thiết bị."""
    device_name = device['name']
    try:
        from core.ssh_client import SSHClient # Import tại đây
        ssh = SSHClient(device, username, password)
        if not ssh.connect():
            results[device_name] = (False, f"Không thể kết nối")
            return
        output = ssh.conn.send_config_set(commands)
        results[device_name] = (True, output)
        ssh.disconnect()
    except Exception as e:
        results[device_name] = (False, str(e))

def run_bulk_config_push():
    """Hàm chính điều phối chức năng đẩy cấu hình hàng loạt theo hãng."""
    while True: # Vòng lặp chính
        clear_screen()
        console.rule("[bold yellow]🚀 Đẩy Cấu hình Hàng loạt[/bold yellow]")

        # 1. Chọn Hãng (Vendor)
        vendors = [d for d in sorted(os.listdir(TEMPLATE_DIR)) if os.path.isdir(os.path.join(TEMPLATE_DIR, d))]
        if not vendors:
            print_error("Không tìm thấy thư mục của hãng nào trong 'core/templates/'."); input("\nNhấn Enter..."); return
        
        print_info("Chọn hãng thiết bị:")
        for i, vendor in enumerate(vendors, 1): print(f" [{i}] {vendor}")
        print("\n [0] Quay lại")
        
        try:
            vendor_choice = int(input("\nChọn hãng (nhập 0 để hủy): ").strip())
            if vendor_choice == 0: break
            chosen_vendor = vendors[vendor_choice - 1]
        except (ValueError, IndexError):
            print_error("Lựa chọn không hợp lệ."); input("\nNhấn Enter..."); continue

        # 2. Chọn Template
        vendor_path = os.path.join(TEMPLATE_DIR, chosen_vendor)
        templates = _load_templates_from_path(vendor_path)
        if not templates:
            print_error(f"Không tìm thấy mẫu nào cho hãng '{chosen_vendor}'."); input("\nNhấn Enter..."); continue
        
        clear_screen(); console.rule(f"[bold yellow]Mẫu cho: {chosen_vendor}[/bold yellow]")
        for i, t in enumerate(templates, 1): print(f" [{i}] {t['name']}")
        print("\n [0] Quay lại")
        try:
            template_choice = int(input("\nChọn mẫu để đẩy (nhập 0 để hủy): ").strip())
            if template_choice == 0: continue
            selected_template = templates[template_choice - 1]
        except (ValueError, IndexError):
            print_error("Lựa chọn không hợp lệ."); input("\nNhấn Enter..."); continue

        # 3. Nhập biến
        variables = {}
        if 'variables' in selected_template:
            for var in selected_template['variables']:
                val = input(f"> {var['prompt']} [mặc định: {var['default']}]: ").strip()
                variables[var['name']] = val if val else var['default']

        # 4. Chọn thiết bị (đã lọc theo hãng)
        all_devices = load_devices()
        vendor_devices = {name: info for name, info in all_devices.items() if info['device_type'] == chosen_vendor}
        if not vendor_devices:
            print_error(f"Không có thiết bị nào thuộc hãng '{chosen_vendor}' trong danh sách."); input("\nNhấn Enter..."); continue

        device_list = list(vendor_devices.items())
        print_info(f"\nCác thiết bị có sẵn của hãng '{chosen_vendor}':")
        for i, (name, _) in enumerate(device_list, 1): print(f" [{i}] {name}")
        target_input = input("\nNhập số thứ tự (1,3,5), 'all', hoặc để trống để hủy: ").strip().lower()
        if not target_input: continue

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
                print_error("Định dạng không hợp lệ."); input("\nNhấn Enter..."); continue
        
        # 5. Xác nhận và Thực thi
        print_warning(f"\nBạn sắp đẩy mẫu '{selected_template['name']}' lên {len(target_devices)} thiết bị.")
        if input("Bạn có chắc chắn muốn tiếp tục? (y/n): ").lower() != 'y': continue

        username, password = load_credentials()
        threads, results = [], {}
        print_info("\nBắt đầu đẩy cấu hình...")
        
        template = Template("\n".join(selected_template['commands'][chosen_vendor]))
        rendered_commands = template.render(variables).splitlines()

        for device in target_devices:
            thread = threading.Thread(target=_push_config_to_device, args=(device, username, password, rendered_commands, results))
            threads.append(thread); thread.start()
        for thread in threads: thread.join()

        # 6. Báo cáo
        console.rule("[bold green]Kết quả[/bold green]")
        for name, (success, output) in results.items():
            if success: print_success(f"✅ {name}: Thành công")
            else: print_error(f"❌ {name}: Thất bại - {output}")
        input("\nNhấn Enter để quay lại menu chính..."); break
