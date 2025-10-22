# modules/web_filter.py
import re
from core.ui import console, create_table, print_info, print_success, print_error
from rich.text import Text

URL_FILTER_ID = "1" # ID của Urlfilter Profile ta đã tạo

def get_rules(ssh):
    """Lấy và phân tích các rule, trả về ID và các thuộc tính khác."""
    output = ssh.run(f"show webfilter urlfilter {URL_FILTER_ID}")
    
    entries_text = re.search(r'config entries(.*?)end', output, re.DOTALL)
    if not entries_text:
        return []

    rules = []
    # Regex mới: tìm các khối 'edit <ID>' và lấy ID là con số
    rule_blocks = re.findall(r'edit\s+(\d+)\n(.*?)\n\s+next', entries_text.group(1), re.DOTALL)
    
    for entry_id, block_content in rule_blocks:
        url = re.search(r'set url "(.*?)"', block_content)
        action = re.search(r'set action (\w+)', block_content)
        status = re.search(r'set status (\w+)', block_content)
        rules.append({
            "id": entry_id,
            "url": url.group(1) if url else "N/A",
            "action": action.group(1) if action else "monitor",
            "status": status.group(1) if status else "enable"
        })
    return rules

def add_rule(ssh, url, action, status):
    """Thêm rule mới với cú pháp FortiOS chính xác."""
    commands = [
        f"config webfilter urlfilter",
        f"edit {URL_FILTER_ID}",
        "config entries",
        "edit 0", # Dùng 'edit 0' để FortiGate tự tạo ID mới
        f"set url \"{url}\"",
        f"set action {action}",
        f"set status {status}",
        "end",
        "end"
    ]
    ssh.run_config_set(commands)
    print_success(f"Đã thêm rule cho '{url}' thành công.")

def delete_rule(ssh, entry_id):
    """Xóa một rule dựa trên ID của nó."""
    commands = [
        f"config webfilter urlfilter",
        f"edit {URL_FILTER_ID}",
        "config entries",
        f"delete {entry_id}", # Xóa theo ID
        "end",
        "end"
    ]
    ssh.run_config_set(commands)
    print_success(f"Đã xóa rule ID {entry_id} thành công.")

def toggle_rule_status(ssh, entry_id, current_status):
    """Bật/tắt một rule dựa trên ID của nó."""
    new_status = "disable" if current_status == "enable" else "enable"
    commands = [
        f"config webfilter urlfilter",
        f"edit {URL_FILTER_ID}",
        "config entries",
        f"edit {entry_id}", # Sửa theo ID
        f"set status {new_status}",
        "end",
        "end"
    ]
    ssh.run_config_set(commands)
    print_success(f"Đã đổi trạng thái rule ID {entry_id} thành '{new_status}'.")

def display_rules_table(rules):
    # ... (Hàm này giữ nguyên) ...
    if not rules: print_info("Chưa có rule nào được cấu hình."); return
    table = create_table("📜 WEB FILTER POLICY", {"ID": "dim", "Website": "cyan", "Hành động": "default", "Trạng thái": "default"})
    for rule in rules:
        action_text = Text(rule['action'].upper(), style="bold red" if rule['action'] == 'block' else "bold green")
        status_text = Text("✅ ACTIVE", style="green") if rule['status'] == 'enable' else Text("⚫ INACTIVE", style="dim")
        table.add_row(rule['id'], rule['url'], action_text, status_text)
    console.print(table)
