# core/snmp_client.py
from easysnmp import Session

def snmp_walk(community, ip, oid, version=2):
    """
    Thực hiện SNMP walk sử dụng thư viện easysnmp.
    Trả về một dictionary {index: value}.
    """
    results = {}
    try:
        session = Session(hostname=ip, community=community, version=version, timeout=10, retries=2)
        
        # Thực hiện walk
        walk_results = session.walk(oid)
        
        for item in walk_results:
            # item.oid sẽ có dạng 'ifName', item.oid_index là '1', item.value là 'FastEthernet0/0'
            index = item.oid_index
            value = item.value
            results[index] = value

    except Exception as e:
        return {'error': str(e)}
            
    return results
