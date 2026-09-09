import ipaddress
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ParsedHop:
    raw: str
    source_host: str | None = None
    source_ip: str | None = None
    destination_host: str | None = None
    protocol: str | None = None
    timestamp: datetime | None = None
    is_private_ip: bool = False
    is_malformed: bool = False
    missing_data: bool = False


# Common Received header patterns. These are heuristic and intentionally conservative.
FROM_RE = re.compile(r"from\s+([^\s\(]+)(?:\s+\(([^\)]*)\))?", re.IGNORECASE)
BY_RE = re.compile(r"by\s+([^\s\(]+)(?:\s+\(([^\)]*)\))?", re.IGNORECASE)
WITH_RE = re.compile(r"with\s+([^\s;]+)", re.IGNORECASE)
IP_RE = re.compile(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b")
IPV6_RE = re.compile(r"\b([0-9a-fA-F:]+:[0-9a-fA-F:]+)\b")
# Date at end of Received: "; Mon, 01 Jan 2024 00:00:00 +0000"
DATE_RE = re.compile(r";\s*(.+)$")


def _extract_ip(text: str) -> str | None:
    m = IP_RE.search(text)
    if m:
        return m.group(1)
    m = IPV6_RE.search(text)
    if m:
        return m.group(1)
    return None


def _is_private_ip(ip_str: str | None) -> bool:
    if not ip_str:
        return False
    try:
        addr = ipaddress.ip_address(ip_str)
        return addr.is_private or addr.is_loopback or addr.is_reserved
    except ValueError:
        return False


def _parse_hop_date(date_str: str) -> datetime | None:
    from email.utils import parsedate_to_datetime

    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return None


def parse_received_chain(received_headers: list[str]) -> list[ParsedHop]:
    """Parse a list of Received headers from newest to oldest.

    Returns hops preserving that order with an index.
    """
    hops: list[ParsedHop] = []
    for idx, raw in enumerate(received_headers):
        raw = raw.strip()
        hop = ParsedHop(raw=raw)

        try:
            from_match = FROM_RE.search(raw)
            by_match = BY_RE.search(raw)
            with_match = WITH_RE.search(raw)
            date_match = DATE_RE.search(raw)

            if from_match:
                hop.source_host = from_match.group(1).strip()
                # Heuristic: if the parenthetical contains an IP, extract it.
                paren = from_match.group(2)
                if paren:
                    ip = _extract_ip(paren)
                    if ip:
                        hop.source_ip = ip
                        hop.is_private_ip = _is_private_ip(ip)

            if by_match:
                hop.destination_host = by_match.group(1).strip()

            if with_match:
                hop.protocol = with_match.group(1).strip().lower()

            if date_match:
                hop.timestamp = _parse_hop_date(date_match.group(1).strip())

            # If no source host or IP was found, mark as missing data.
            if not hop.source_host and not hop.source_ip:
                hop.missing_data = True

        except Exception:
            hop.is_malformed = True

        hops.append(hop)

    return hops
