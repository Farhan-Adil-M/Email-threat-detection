import ipaddress
import socket

import dns.exception
import dns.resolver

from app.services.intelligence.contracts import IntelligenceProvider, NormalizedIntelResult


def normalize_indicator(indicator: str, indicator_type: str) -> str:
    value = indicator.strip().lower().rstrip(".")
    if indicator_type == "domain":
        try:
            value = value.encode("idna").decode("ascii")
        except UnicodeError:
            pass
    return value


class DisabledProvider(IntelligenceProvider):
    name = "disabled"

    def lookup(self, indicator: str, indicator_type: str) -> NormalizedIntelResult:
        return NormalizedIntelResult(self.name, "disabled", indicator, indicator_type)


class FixtureProvider(IntelligenceProvider):
    name = "fixture"

    def lookup(self, indicator: str, indicator_type: str) -> NormalizedIntelResult:
        normalized = normalize_indicator(indicator, indicator_type)
        data = {"mode": "deterministic", "note": "No live provider queried."}
        return NormalizedIntelResult(
            self.name, "fixture", normalized, indicator_type, data, 0.5, "synthetic-fixture", False
        )


class DNSProvider(IntelligenceProvider):
    name = "dns"

    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout

    def lookup(self, indicator: str, indicator_type: str) -> NormalizedIntelResult:
        normalized = normalize_indicator(indicator, indicator_type)
        if indicator_type != "domain":
            return NormalizedIntelResult(self.name, "disabled", normalized, indicator_type)
        data: dict[str, list[str]] = {}
        status = "success"
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.timeout
            resolver.lifetime = self.timeout
            for record_type in ("A", "AAAA", "MX", "NS", "TXT"):
                try:
                    answers = resolver.resolve(normalized, record_type)
                    data[record_type] = [answer.to_text().strip('"') for answer in answers][:25]
                except (dns.exception.DNSException, socket.gaierror):
                    data[record_type] = []
        except Exception:
            status = "error"
        return NormalizedIntelResult(self.name, status, normalized, indicator_type, data, 0.85, "system-resolver")
