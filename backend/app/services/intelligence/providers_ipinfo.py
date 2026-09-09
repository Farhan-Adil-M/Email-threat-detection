"""IP geolocation and ASN provider adapter.

Queries ip-api.com (free, no API key, 45 req/min) for IP geolocation and ASN data.
Returns "Estimated geolocation" — never claims exact attacker location.
Graceful failure on timeout/unavailability.
"""
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

from app.services.intelligence.contracts import IntelligenceProvider, NormalizedIntelResult
from app.services.intelligence.providers import normalize_indicator


class IPInfoProvider(IntelligenceProvider):
    name = "ip-api"

    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout

    def lookup(self, indicator: str, indicator_type: str) -> NormalizedIntelResult:
        normalized = normalize_indicator(indicator, indicator_type)
        if indicator_type != "ip":
            return NormalizedIntelResult(
                provider=self.name, status="skipped",
                indicator=normalized, indicator_type=indicator_type,
                data={"reason": "IP-API only supports IP indicators"},
                source_reference="ip-api.com",
            )

        data: dict = {}
        status = "success"
        try:
            url = f"http://ip-api.com/json/{normalized}?fields=status,message,country,regionName,city,lat,lon,isp,org,as,asname,reverse"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = json.loads(resp.read())
                if raw.get("status") == "success":
                    data = {
                        "country": raw.get("country"),
                        "region": raw.get("regionName"),
                        "city": raw.get("city"),
                        "latitude": raw.get("lat"),
                        "longitude": raw.get("lon"),
                        "isp": raw.get("isp"),
                        "organization": raw.get("org"),
                        "asn": raw.get("as"),
                        "asname": raw.get("asname"),
                        "reverse_dns": raw.get("reverse"),
                        "geolocation_note": "Estimated geolocation based on observed source IP. Does not establish attacker identity.",
                    }
                else:
                    status = "not_found"
                    data = {"reason": raw.get("message", "Query failed")}
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            status = "error"
            data = {"reason": str(e)}
        except Exception as e:
            status = "error"
            data = {"reason": str(e)}

        return NormalizedIntelResult(
            provider=self.name, status=status,
            indicator=normalized, indicator_type=indicator_type,
            data=data,
            confidence=0.5 if status == "success" else 0.0,
            source_reference="ip-api.com",
            raw_available=(status == "success"),
        )
