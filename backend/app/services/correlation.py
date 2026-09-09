import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.campaign import Campaign, CampaignMembership
from app.models.email import EmailMessage
from app.models.url_indicator import URLIndicator


class CorrelationService:
    def __init__(self, db: Session): self.db = db

    def correlate(self, case_id: UUID) -> Campaign | None:
        current_urls = {u.hostname for u in self.db.query(URLIndicator).filter(URLIndicator.case_id == case_id).all() if u.hostname}
        current_email = self.db.query(EmailMessage).filter(EmailMessage.case_id == case_id).first()
        current_domains = set()
        if current_email:
            for address in (current_email.from_address, current_email.reply_to, current_email.return_path):
                if address and "@" in address: current_domains.add(address.rsplit("@", 1)[1].lower())
        if not current_urls and not current_domains: return None
        matches: list[tuple[UUID, list[str]]] = []
        for other in self.db.query(EmailMessage).filter(EmailMessage.case_id != case_id).all():
            other_domains = {a.rsplit("@", 1)[1].lower() for a in (other.from_address, other.reply_to, other.return_path) if a and "@" in a}
            shared = sorted(current_domains & other_domains)
            if shared: matches.append((other.case_id, [f"domain:{x}" for x in shared]))
        for other_url in self.db.query(URLIndicator).filter(URLIndicator.case_id != case_id).all():
            if other_url.hostname in current_urls: matches.append((other_url.case_id, [f"url-host:{other_url.hostname}"]))
        if not matches: return None
        campaign = Campaign(name=f"Possible campaign for case {case_id}", description="Possible relationship based on shared observable infrastructure; not confirmed attribution.", confidence=0.65)
        self.db.add(campaign); self.db.flush()
        self.db.add(CampaignMembership(campaign_id=campaign.id, case_id=case_id, confidence=0.65, evidence_refs=json.dumps([str(case_id)])))
        for matched_case, refs in matches:
            self.db.add(CampaignMembership(campaign_id=campaign.id, case_id=matched_case, confidence=0.65, evidence_refs=json.dumps(refs)))
        self.db.commit(); self.db.refresh(campaign)
        return campaign
