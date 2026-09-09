from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.case import Case
from app.models.finding import Finding
from app.models.campaign import Campaign, CampaignMembership, MitreMapping
from app.models.threat_intel import ThreatIntelResult
from app.models.risk_assessment import RiskAssessment
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(Case).count()
    open_cases = db.query(Case).filter(
        Case.status.notin_(["RESOLVED", "FALSE_POSITIVE"])
    ).count()

    severity_counts = {}
    for sev, count in db.query(Case.severity, func.count(Case.id)).group_by(Case.severity).all():
        severity_counts[sev or "unassigned"] = count

    status_counts = {}
    for st, count in db.query(Case.status, func.count(Case.id)).group_by(Case.status).all():
        status_counts[st] = count

    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    campaign_list = []
    for c in campaigns:
        member_count = db.query(CampaignMembership).filter(CampaignMembership.campaign_id == c.id).count()
        campaign_list.append({
            "id": str(c.id),
            "name": c.name,
            "description": c.description,
            "confidence": c.confidence,
            "case_count": member_count,
            "created_at": c.created_at.isoformat(),
        })

    indicators = db.query(ThreatIntelResult).all()
    unique_domains = set()
    unique_ips = set()
    unique_urls = set()
    for ind in indicators:
        if ind.indicator_type == "domain":
            unique_domains.add(ind.indicator)
        elif ind.indicator_type == "ip":
            unique_ips.add(ind.indicator)
        elif ind.indicator_type == "url":
            unique_urls.add(ind.indicator)

    mitre_techniques = {}
    for m in db.query(MitreMapping).all():
        mitre_techniques[m.technique] = mitre_techniques.get(m.technique, 0) + 1

    risk_dist = {"low": 0, "guarded": 0, "medium": 0, "high": 0, "critical": 0}
    for r in db.query(RiskAssessment).all():
        level = r.risk_level or "low"
        if level in risk_dist:
            risk_dist[level] += 1

    recent = db.query(Case).order_by(Case.created_at.desc()).limit(10).all()

    return APIResponse(data={
        "total_cases": total,
        "open_cases": open_cases,
        "severity_counts": severity_counts,
        "status_counts": status_counts,
        "campaigns": campaign_list,
        "indicators": {
            "total": len(indicators),
            "unique_domains": len(unique_domains),
            "unique_ips": len(unique_ips),
            "unique_urls": len(unique_urls),
            "top_domains": list(unique_domains)[:10],
            "top_ips": list(unique_ips)[:10],
        },
        "mitre_techniques": mitre_techniques,
        "risk_distribution": risk_dist,
        "recent_cases": [
            {"id": str(c.id), "title": c.title, "status": c.status, "severity": c.severity, "created_at": c.created_at.isoformat()}
            for c in recent
        ],
    })
