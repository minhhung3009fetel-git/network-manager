# core/vendors/vendor_factory.py
from .vendor_cisco import CiscoDevice
from .vendor_fortinet import FortinetDevice
# Import các vendor khác ở đây khi bạn thêm chúng
# from .vendor_mikrotik import MikrotikDevice 

VENDOR_MAP = {
    "cisco_ios": CiscoDevice,
    "cisco_nxos": CiscoDevice, # Giả sử dùng chung lớp
    "fortinet": FortinetDevice,
    # "mikrotik_routeros": MikrotikDevice,
}

def get_vendor_class(device_type):
    """
    Trả về class vendor phù hợp dựa trên device_type.
    """
    for key, vendor_class in VENDOR_MAP.items():
        if key in device_type:
            return vendor_class
    return None
