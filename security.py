import ipaddress
import socket
from urllib.parse import urlparse
from fastapi import HTTPException

# Blocked IP ranges (SSRF Protection)
PRIVATE_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10")
]

def validate_url(url: str) -> str:
    parsed = urlparse(url)
    
    # Allowed Protocols Filter
    if parsed.scheme not in ["http", "https"]:
        raise HTTPException(status_code=400, detail="Only HTTP and HTTPS protocols are allowed.")
    
    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="Invalid URL hostname.")
        
    # Resolve IP address to check against private/internal ranges
    try:
        ip_addr = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_addr)
        for net in PRIVATE_NETWORKS:
            if ip in net:
                raise HTTPException(status_code=403, detail="Access to local or private network URLs is strictly blocked.")
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="Could not resolve domain name.")
        
    return url