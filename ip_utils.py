# ip_utils.py

import ipaddress
from db import get_all_records

def get_all_hosts(subnet):
    """
    Subnet içindeki tüm kullanılabilir host IP'lerini listeler.
    Örnek: '10.26.1.0/24' ➜ ['10.26.1.1', ..., '10.26.1.254']
    """
    try:
        net = ipaddress.ip_network(subnet, strict=False)
        return [str(ip) for ip in net.hosts()]
    except ValueError as e:
        print(f"[HATA] Subnet hatalı: {e}")
        return []

def get_unused_ips(subnet, used_ips):
    """
    Subnet içerisindeki kullanılmayan IP adreslerini döner.
    """
    all_hosts = get_all_hosts(subnet)
    return [ip for ip in all_hosts if ip not in used_ips]

def find_unused_ips(subnet, used_ips):
    """
    Geri uyumluluk için eski ad. get_unused_ips ile aynıdır.
    """
    return get_unused_ips(subnet, used_ips)

def get_subnet_info(subnet):
    """
    Subnet hakkında detaylı bilgi döner:
    - Ağ adresi
    - Broadcast adresi
    - Subnet maskesi
    - Toplam IP
    - Kullanılabilir IP aralığı vs.
    """
    try:
        net = ipaddress.ip_network(subnet, strict=False)
        hosts = list(net.hosts())
        usable_range = f"{hosts[0]} - {hosts[-1]}" if len(hosts) >= 2 else "Yok"

        return {
            "Ağ Adresi": str(net.network_address),
            "Broadcast": str(net.broadcast_address),
            "Subnet Mask": str(net.netmask),
            "Toplam IP": net.num_addresses,
            "Kullanılabilir IP": max(0, net.num_addresses - 2),
            "Kullanılabilir Aralık": usable_range
        }
    except ValueError as e:
        print(f"[HATA] Subnet hatalı: {e}")
        return {}

def is_valid_ip(ip_str):
    """
    IP adresi geçerli mi?
    """
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def is_valid_subnet(subnet_str):
    """
    CIDR formatındaki subnet geçerli mi?
    """
    try:
        ipaddress.ip_network(subnet_str, strict=False)
        return True
    except ValueError:
        return False

def get_used_ips_in_subnet(subnet_cidr):
    """
    Veritabanındaki tüm kayıtlar arasında, belirli bir subnet içerisinde kalan
    kullanılan IP'leri döner. (inside_ip_gateway alanına göre)
    """
    try:
        net = ipaddress.ip_network(subnet_cidr, strict=False)
        used = []

        for rec in get_all_records():
            ip = rec.get('inside_ip_gateway')
            if ip and is_valid_ip(ip) and ipaddress.ip_address(ip) in net:
                used.append(ip)

        return used
    except Exception as e:
        print(f"[HATA] get_used_ips_in_subnet: {e}")
        return []

# --- Test Amaçlı Demo Kullanım ---
if __name__ == "__main__":
    test_subnet = "10.26.1.0/24"
    used_ips = ["10.26.1.1", "10.26.1.2", "10.26.1.100", "10.26.1.200"]

    print("\n📌 Tüm host IP'leri:")
    all_hosts = get_all_hosts(test_subnet)
    print(all_hosts[:5], "...", all_hosts[-5:])

    print("\n📌 Boş IP'ler:")
    unused = get_unused_ips(test_subnet, used_ips)
    print(unused[:5], "...", unused[-5:])

    print("\n📌 Subnet Bilgisi:")
    for k, v in get_subnet_info(test_subnet).items():
        print(f"{k}: {v}")

    print("\n📌 Doğrulama:")
    print("IP 10.26.1.15 geçerli mi?", is_valid_ip("10.26.1.15"))
    print("Subnet 10.26.1.0/24 geçerli mi?", is_valid_subnet("10.26.1.0/24"))
    print("Subnet 10.26.1.0/33 geçerli mi?", is_valid_subnet("10.26.1.0/33"))
