
import ipaddress
import socket
from urllib.parse import urlparse

from fastapi import HTTPException


ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_PORTS = {80, 443}


def _is_public_ip(address: str) -> bool:
    """
    Return True only for globally routable IP addresses.
    This rejects private, loopback, link-local, multicast,
    reserved, and other non-public address ranges.
    """
    ip = ipaddress.ip_address(address)

    # IPv4-mapped IPv6 addresses should be checked as IPv4.
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped

    return ip.is_global


def validate_url(url: str) -> str:
    """
    Validate a user-supplied HTTP(S) URL before requesting it.

    Returns the original URL when valid.
    Raises HTTPException when the URL is invalid or resolves
    to any non-public IP address.
    """
    if not isinstance(url, str) or not url.strip():
        raise HTTPException(
            status_code=400,
            detail="A valid URL is required.",
        )

    url = url.strip()

    try:
        parsed = urlparse(url)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid URL.",
        )

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise HTTPException(
            status_code=400,
            detail="Only HTTP and HTTPS protocols are allowed.",
        )

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(
            status_code=400,
            detail="Invalid URL hostname.",
        )

    # Reject URLs containing embedded credentials, e.g. user:pass@host.
    if parsed.username is not None or parsed.password is not None:
        raise HTTPException(
            status_code=400,
            detail="URLs containing credentials are not allowed.",
        )

    # Restrict ports to standard web ports.
    try:
        port = parsed.port
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid URL port.",
        )

    if port is not None and port not in ALLOWED_PORTS:
        raise HTTPException(
            status_code=400,
            detail="Only standard HTTP/HTTPS ports are allowed.",
        )

    hostname = hostname.rstrip(".").lower()

    if not hostname:
        raise HTTPException(
            status_code=400,
            detail="Invalid URL hostname.",
        )

    # Reject localhost-style names before DNS resolution.
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise HTTPException(
            status_code=403,
            detail="Access to localhost is blocked.",
        )

    # If the hostname is already an IP literal, validate it directly.
    try:
        literal_ip = ipaddress.ip_address(hostname)
    except ValueError:
        literal_ip = None

    if literal_ip is not None:
        if not _is_public_ip(str(literal_ip)):
            raise HTTPException(
                status_code=403,
                detail="Access to local, private, or non-public IP addresses is blocked.",
            )
        return url

    # Resolve both IPv4 and IPv6. Reject the hostname if ANY
    # returned address is non-public.
    try:
        address_info = socket.getaddrinfo(
            hostname,
            port or (443 if parsed.scheme.lower() == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror:
        raise HTTPException(
            status_code=400,
            detail="Could not resolve domain name.",
        )
    except OSError:
        raise HTTPException(
            status_code=400,
            detail="Could not resolve domain name.",
        )

    if not address_info:
        raise HTTPException(
            status_code=400,
            detail="Domain name did not resolve to an IP address.",
        )

    resolved_addresses = {
        result[4][0]
        for result in address_info
        if result and result[4]
    }

    if not resolved_addresses:
        raise HTTPException(
            status_code=400,
            detail="Domain name did not resolve to an IP address.",
        )

    for address in resolved_addresses:
        try:
            if not _is_public_ip(address):
                raise HTTPException(
                    status_code=403,
                    detail="Access to local, private, or non-public IP addresses is blocked.",
                )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Domain resolved to an invalid IP address.",
            )

    return url
