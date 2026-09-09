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


class ChainedProvider(IntelligenceProvider):
    """Chains DNS → IPInfo for IPs, and DNS → RDAP for domain registration.

    For domains: DNS resolves IPs, then IPInfo enriches each IP, RDAP gets registration.
    For IPs: IPInfo directly.
    System still works if any single provider fails.
    """
    name = "chained"

    def __init__(self, dns_timeout: float = 2.0, ipinfo_timeout: float = 2.0, rdap_timeout: float = 3.0):
        from app.services.intelligence.providers_ipinfo import IPInfoProvider
        from app.services.intelligence.providers_rdap import RDAPProvider
        self.dns = DNSProvider(dns_timeout)
        self.ipinfo = IPInfoProvider(ipinfo_timeout)
        self.rdap = RDAPProvider(rdap_timeout)

    def lookup(self, indicator: str, indicator_type: str) -> NormalizedIntelResult:
        normalized = normalize_indicator(indicator, indicator_type)

        if indicator_type == "ip":
            return self.ipinfo.lookup(normalized, "ip")

        if indicator_type != "domain":
            return NormalizedIntelResult(
                provider=self.name, status="skipped",
                indicator=normalized, indicator_type=indicator_type,
                data={"reason": "ChainedProvider supports domain and ip indicators"},
            )

        dns_result = self.dns.lookup(normalized, "domain")
        combined_data: dict = {
            "dns": dns_result.data if dns_result.status == "success" else {"status": dns_result.status},
        }

        resolved_ips: list[str] = []
        if dns_result.status == "success":
            for record_type in ("A", "AAAA"):
                for answer in dns_result.data.get(record_type, []):
                    ip = answer.split()[0] if " " in answer else answer
                    if _is_valid_public_ip(ip):
                        resolved_ips.append(ip)

        ip_results: list[dict] = []
        for ip in resolved_ips[:5]:
            ip_result = self.ipinfo.lookup(ip, "ip")
            ip_results.append({
                "ip": ip,
                "provider": ip_result.provider,
                "status": ip_result.status,
                "data": ip_result.data,
                "confidence": ip_result.confidence,
            })
        if ip_results:
            combined_data["ip_enrichment"] = ip_results

        rdap_result = self.rdap.lookup(normalized, "domain")
        combined_data["rdap"] = rdap_result.data if rdap_result.status == "success" else {"status": rdap_result.status}

        overall_status = "success" if dns_result.status == "success" else dns_result.status
        overall_confidence = dns_result.confidence
        if ip_results:
            avg_ip_conf = sum(r["confidence"] for r in ip_results) / len(ip_results)
            overall_confidence = max(overall_confidence, avg_ip_conf)

        return NormalizedIntelResult(
            provider=self.name, status=overall_status,
            indicator=normalized, indicator_type="domain",
            data=combined_data,
            confidence=overall_confidence,
            source_reference="chained-dns-rdap-ipinfo",
            raw_available=(dns_result.status == "success"),
        )


def _is_valid_public_ip(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
        return not addr.is_private and not addr.is_loopback and not addr.is_reserved and not addr.is_link_local
    except ValueError:
        return False
