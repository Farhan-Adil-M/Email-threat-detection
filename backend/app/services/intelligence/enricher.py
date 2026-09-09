import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.config import settings
from app.models.email import EmailMessage
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
            self.provider = DNSProvider(settings.INTEL_DNS_TIMEOUT)
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
        return list(dict.fromkeys(values))[:50]

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
