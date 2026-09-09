import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.config import settings
from app.models.email import EmailMessage
from app.models.received_hop import ReceivedHop
from app.models.threat_intel import ThreatIntelResult
from app.models.url_indicator import URLIndicator
from app.services.intelligence.contracts import NormalizedIntelResult
from app.services.intelligence.providers import DNSProvider, DisabledProvider, FixtureProvider


class IntelligenceEnricher:
    def __init__(self, db: Session):
        self.db = db
        mode = settings.INTEL_MODE.lower()
        if mode == "fixture":
            self.provider = FixtureProvider()
        elif mode == "live":
            from app.services.intelligence.providers import ChainedProvider
            self.provider = ChainedProvider(
                dns_timeout=settings.INTEL_DNS_TIMEOUT,
                ipinfo_timeout=getattr(settings, "INTEL_IPINFO_TIMEOUT", 2.0),
                rdap_timeout=getattr(settings, "INTEL_RDAP_TIMEOUT", 3.0),
            )
        else:
            self.provider = DisabledProvider()

    def _indicators(self, case_id: UUID) -> list[tuple[str, str]]:
        values: list[tuple[str, str]] = []
        emails = self.db.query(EmailMessage).filter(EmailMessage.case_id == case_id).all()
        for email in emails:
            for address in (email.from_address, email.reply_to, email.return_path):
                if address and "@" in address:
                    values.append((address.rsplit("@", 1)[1], "domain"))
        urls = self.db.query(URLIndicator).filter(URLIndicator.case_id == case_id).all()
        values.extend((url.hostname, "domain") for url in urls if url.hostname)
        hops = self.db.query(ReceivedHop).filter(
            ReceivedHop.case_id == case_id,
            ReceivedHop.source_ip.is_not(None),
            ReceivedHop.is_private_ip == False,
        ).all()
        for hop in hops:
            if hop.source_ip:
                values.append((hop.source_ip, "ip"))
        seen: dict[tuple[str, str], None] = {}
        deduped: list[tuple[str, str]] = []
        for item in values:
            key = (item[0].strip().lower(), item[1])
            if key not in seen:
                seen[key] = None
                deduped.append(item)
        return deduped[:50]

    def enrich_case(self, case_id: UUID) -> list[ThreatIntelResult]:
        results: list[ThreatIntelResult] = []
        for indicator, indicator_type in self._indicators(case_id):
            normalized: NormalizedIntelResult = self.provider.lookup(indicator, indicator_type)
            row = ThreatIntelResult(
                case_id=case_id,
                indicator=normalized.indicator,
                indicator_type=normalized.indicator_type,
                provider=normalized.provider,
                status=normalized.status,
                data_json=json.dumps(normalized.data, sort_keys=True),
                confidence=normalized.confidence,
                source_reference=normalized.source_reference,
                raw_available=normalized.raw_available,
                queried_at=normalized.queried_at,
            )
            self.db.add(row)
            results.append(row)
        self.db.commit()
        return results
