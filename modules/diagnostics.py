# modules/diagnostics.py
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from core.devices import load_devices
from core.utils import clear_screen, is_device_reachable
from core.ui import console, print_info, print_error, print_warning, print_success, Panel
from core.snmp_client import snmp_walk

def _ping_test(ip):
    return os.system(f"ping -c 1 -W 2 {ip} > /dev/null 2>&1") == 0

def _format_report(device, steps, conclusion, suggestion):
    report_string = ""
    report_string += f"  Thiết bị:         {device['name']} ({device['ip']})\n"
    report_string += f"  Thời gian:        {datetime.now(tz=ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report_string += "  " + "-"*30 + " CÁC BƯỚC KIỂM TRA " + "-"*30 + "\n\n"
    
    for step in steps:
        report_string += f"   - {step}\n"
        
    report_string += "\n  " + "-"*30 + " KẾT LUẬN & GỢI Ý " + "-"*31 + "\n\n"
    report_string += f"  💡 {conclusion}\n\n"
    report_string += f"  ➡️  {suggestion}"
    console.print(Panel(report_string, title="🩺 BÁO CÁO CHẨN ĐOÁN SỰ CỐ", border_style="bold blue"))

def _snmp_deep_dive(device):
    snmp_community = os.getenv("SNMP_COMMUNITY", "public")
    steps = [f"[bold green][PASS][/bold green] Kết nối Ping thành công."]
    problems_found = []

    print_info("Thiết bị đang UP. Bắt đầu kiểm tra chuyên sâu bằng SNMP...")
    
    IF_NAME_OID = '1.3.6.1.2.1.31.1.1.1.1'
    IF_OPER_STATUS_OID = '1.3.6.1.2.1.2.2.1.8'
    IF_IN_ERRORS_OID = '1.3.6.1.2.1.2.2.1.14'
    IF_OUT_ERRORS_OID = '1.3.6.1.2.1.2.2.1.20'

    if_names = snmp_walk(snmp_community, device['ip'], IF_NAME_OID)
    if 'error' in if_names:
        steps.append(f"[bold red][FAIL][/bold red] Kết nối SNMP thất bại. Lý do: {if_names['error']}")
        _format_report(device, steps, "Không thể thực hiện chẩn đoán SNMP.", "Kiểm tra lại cấu hình SNMP trên thiết bị và community string trong file .env.")
        return

    steps.append(f"[bold green][PASS][/bold green] Kết nối SNMP và lấy danh sách interface thành công.")
    
    if_statuses = snmp_walk(snmp_community, device['ip'], IF_OPER_STATUS_OID)
    if_in_errors = snmp_walk(snmp_community, device['ip'], IF_IN_ERRORS_OID)
    if_out_errors = snmp_walk(snmp_community, device['ip'], IF_OUT_ERRORS_OID)

    for index, name in if_names.items():
        if index == 'error': continue
        status = if_statuses.get(index)
        if status == '2' or (status and 'down' in status.lower()):
            problem = f"Interface [bold magenta]{name}[/bold magenta] đang ở trạng thái [bold red]DOWN[/bold red]."
            problems_found.append(problem)
            steps.append(f"[bold red][FAIL][/bold red] Trạng thái cổng {name}: down")
        
        in_errors = int(if_in_errors.get(index, 0))
        out_errors = int(if_out_errors.get(index, 0))
        if in_errors > 0 or out_errors > 0:
            problem = f"Interface [bold magenta]{name}[/bold magenta] có [bold yellow]{in_errors} lỗi đầu vào[/bold yellow] và [bold yellow]{out_errors} lỗi đầu ra[/bold yellow]."
            problems_found.append(problem)
            steps.append(f"[bold yellow][WARN][/bold yellow] Phát hiện gói tin lỗi trên cổng {name}.")

    if not problems_found:
        conclusion = "Kiểm tra SNMP hoàn tất. Không tìm thấy vấn đề rõ ràng ở các interface."
        suggestion = "Thiết bị có vẻ hoạt động bình thường ở tầng liên kết dữ liệu."
    else:
        conclusion = "Phát hiện một số vấn đề ở các interface của thiết bị."
        suggestion = "Vui lòng kiểm tra các vấn đề đã được liệt kê:\n" + "\n".join([f"     - {p}" for p in problems_found])
        
    _format_report(device, steps, conclusion, suggestion)

def run_diagnostics():
    clear_screen()
    console.rule("[bold yellow]🩺 Chẩn đoán Sự cố Thiết bị[/bold yellow]")
    devices = load_devices()
    if not devices: print_warning("Chưa có thiết bị."); return
    device_list = list(devices.items())
    for i, (name, info) in enumerate(device_list, 1): print(f" [{i}] {name} ({info['ip']})")
    print("\n [0] Quay lại")

    try:
        choice = int(input("\nChọn thiết bị để chẩn đoán: ").strip())
        if choice == 0: print_info("Đã hủy."); return
        name, info = device_list[choice - 1]
        target_device = {'name': name, **info}
    except (ValueError, IndexError):
        print_error("Lựa chọn không hợp lệ."); return

    print_info(f"\nBắt đầu chẩn đoán cho {target_device['name']}...")
    is_up = is_device_reachable(target_device['ip'])
    if not is_up:
        print_info("Thiết bị không thể truy cập. Bắt đầu chẩn đoán kết nối mạng...")
        gateway_ip = "10.10.0.1" if target_device['name'].upper().startswith("HN") else "1.1.1.1"
        steps = []; steps.append(f"[bold red][FAIL][/bold red] Ping đến {target_device['name']} ({target_device['ip']})")
        ping_gateway_ok = _ping_test(gateway_ip)
        steps.append(f"[bold green][PASS][/bold green] Ping đến Gateway ({gateway_ip})" if ping_gateway_ok else f"[bold red][FAIL][/bold red] Ping đến Gateway ({gateway_ip})")
        ping_internet_ok = _ping_test("8.8.8.8")
        steps.append(f"[bold green][PASS][/bold green] Ping đến Internet (8.8.8.8)" if ping_internet_ok else f"[bold red][FAIL][/bold red] Ping đến Internet (8.8.8.8)")
        if not ping_gateway_ok: conclusion = "Sự cố hạ tầng mạng Core."; suggestion = "Kiểm tra kết nối và trạng thái của Gateway."
        elif not ping_internet_ok: conclusion = "Sự cố mất kết nối Internet toàn chi nhánh."; suggestion = "Kiểm tra trạng thái WAN trên Router."
        else: conclusion = f"Sự cố cục bộ tại thiết bị đích ({target_device['name']})."; suggestion = "Kiểm tra nguồn, cáp mạng của thiết bị."
        _format_report(target_device, steps, conclusion, suggestion)
    else:
        _snmp_deep_dive(target_device)
