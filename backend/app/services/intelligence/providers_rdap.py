"""RDAP (Registration Data Access Protocol) provider adapter.

Queries rdap.org for domain registration data (registrar, creation date, status).
No API key required. Graceful failure on timeout/unavailability.
"""
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

from app.services.intelligence.contracts import IntelligenceProvider, NormalizedIntelResult
from app.services.intelligence.providers import normalize_indicator


class RDAPProvider(IntelligenceProvider):
    name = "rdap"

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    def lookup(self, indicator: str, indicator_type: str) -> NormalizedIntelResult:
        normalized = normalize_indicator(indicator, indicator_type)
        if indicator_type != "domain":
            return NormalizedIntelResult(
                provider=self.name, status="skipped",
                indicator=normalized, indicator_type=indicator_type,
                data={"reason": "RDAP only supports domain indicators"},
                source_reference="rdap.org",
            )

        data: dict = {}
        status = "success"
        try:
            url = f"https://rdap.org/domain/{normalized}"
            req = urllib.request.Request(url, headers={"Accept": "application/rdap+json"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = json.loads(resp.read())
                data = self._parse_rdap(raw)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                status = "not_found"
                data = {"reason": f"Domain {normalized} not found in RDAP"}
            else:
                status = "error"
                data = {"reason": f"HTTP {e.code}"}
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
            confidence=0.7 if status == "success" else 0.0,
            source_reference="rdap.org",
            raw_available=(status == "success"),
        )

    def _parse_rdap(self, raw: dict) -> dict:
        result: dict = {}
        if "handle" in raw:
            result["handle"] = raw["handle"]
        if "ldhName" in raw:
            result["domain_name"] = raw["ldhName"]
        statuses = raw.get("status", [])
        if statuses:
            result["status"] = statuses
        events = raw.get("events", [])
        for event in events:
            if event.get("eventAction") == "registration":
                result["registration_date"] = event.get("eventDate")
            elif event.get("eventAction") == "expiration":
                result["expiration_date"] = event.get("eventDate")
        entities = raw.get("entities", [])
        for entity in entities:
            roles = entity.get("roles", [])
            if "registrar" in roles:
                vcard = entity.get("vcardArray", [None, []])
                if len(vcard) > 1:
                    for item in vcard[1]:
                        if item[0] == "fn":
                            result["registrar"] = item[3]
                            break
                if not result.get("registrar") and "handle" in entity:
                    result["registrar"] = entity["handle"]
        nameservers = raw.get("nameservers", [])
        if nameservers:
            result["nameservers"] = [ns.get("ldhName", "") for ns in nameservers if ns.get("ldhName")]
        return result
