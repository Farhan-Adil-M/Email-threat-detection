import ipaddress
import re
from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit

from app.services.forensics.header_analyzer import HeaderFinding


URL_RE = re.compile(r"(?i)\b(?:https?|ftp)://[^\s<>\"']+")


@dataclass
class URLAnalysis:
    raw_url: str
    normalized_url: str
    scheme: str | None
    hostname: str | None
    port: int | None
    path: str | None
    has_userinfo: bool = False
    is_ip_literal: bool = False
    is_punycode: bool = False
    findings: list[HeaderFinding] = field(default_factory=list)


def extract_urls(*texts: str | None) -> list[str]:
    seen: set[str] = set()
    urls: list[str] = []
    for text in texts:
        if not text:
            continue
        for match in URL_RE.findall(text):
            candidate = match.rstrip(".,;:!?)]}")
            if candidate not in seen:
                seen.add(candidate)
                urls.append(candidate)
    return urls


def analyze_url(raw_url: str) -> URLAnalysis:
    raw_url = raw_url.strip()
    try:
        parts = urlsplit(raw_url)
        hostname = parts.hostname.lower() if parts.hostname else None
        normalized = urlunsplit((parts.scheme.lower(), parts.netloc, parts.path or "/", parts.query, ""))
        has_userinfo = bool(parts.username or parts.password)
        is_ip_literal = False
        if hostname:
            try:
                ipaddress.ip_address(hostname)
                is_ip_literal = True
            except ValueError:
                pass
        is_punycode = bool(hostname and any(label.startswith("xn--") for label in hostname.split(".")))
        result = URLAnalysis(
            raw_url=raw_url,
            normalized_url=normalized,
            scheme=parts.scheme.lower() or None,
            hostname=hostname,
            port=parts.port,
            path=parts.path or "/",
            has_userinfo=has_userinfo,
            is_ip_literal=is_ip_literal,
            is_punycode=is_punycode,
        )
    except ValueError:
        return URLAnalysis(raw_url, raw_url, None, None, None, None, findings=[
            HeaderFinding("URL-MALFORMED-001", "URL", "medium", "Malformed URL", "URL could not be parsed safely.", {"url": raw_url}, 8, 0.95)
        ])

    if result.scheme not in ("http", "https"):
        result.findings.append(HeaderFinding("URL-UNUSUAL-SCHEME-001", "URL", "medium", "Unusual URL scheme", "URL uses a scheme outside normal web navigation.", {"scheme": result.scheme, "url": raw_url}, 10, 0.9))
    if result.has_userinfo:
        result.findings.append(HeaderFinding("URL-USERINFO-001", "URL", "high", "URL contains embedded user information", "Userinfo in a URL can obscure the real destination hostname.", {"url": raw_url, "hostname": result.hostname}, 15, 0.9))
    if result.is_ip_literal:
        result.findings.append(HeaderFinding("URL-IP-LITERAL-001", "URL", "high", "URL uses an IP address instead of a domain", "The URL destination is an IP literal, which reduces domain identity transparency.", {"url": raw_url, "ip": result.hostname}, 12, 0.85))
    if result.is_punycode:
        result.findings.append(HeaderFinding("URL-PUNYCODE-001", "URL", "medium", "URL contains a punycode hostname", "Punycode may represent an internationalized domain and warrants lookalike review.", {"url": raw_url, "hostname": result.hostname}, 8, 0.75))
    if result.port not in (None, 80, 443):
        result.findings.append(HeaderFinding("URL-UNUSUAL-PORT-001", "URL", "medium", "URL uses an unusual port", "The URL specifies a non-standard web port.", {"url": raw_url, "port": result.port}, 8, 0.85))
    if result.hostname and result.hostname.count(".") >= 4:
        result.findings.append(HeaderFinding("URL-DEEP-HOSTNAME-001", "URL", "low", "URL has an unusually deep hostname", "Deep subdomain nesting can be used to make a destination resemble a trusted name.", {"hostname": result.hostname}, 4, 0.65))
    return result


def analyze_urls(urls: list[str]) -> tuple[list[URLAnalysis], list[HeaderFinding]]:
    analyses = [analyze_url(url) for url in urls]
    findings = [finding for analysis in analyses for finding in analysis.findings]
    return analyses, findings
