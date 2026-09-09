import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class HeaderFinding:
    rule_id: str
    category: str
    severity: str
    title: str
    description: str
    evidence: dict[str, Any] = field(default_factory=dict)
    score_delta: int = 0
    confidence: float = 1.0


def _domain_of(addr: str | None) -> str | None:
    if not addr or "@" not in addr:
        return None
    return addr.split("@")[-1].strip().lower()


def _display_suspicious(display_name: str | None) -> bool:
    if not display_name:
        return False
    lower = display_name.lower()
    executive_terms = ["ceo", "cfo", "cto", "president", "director", "executive", "manager"]
    return any(term in lower for term in executive_terms)


def _lookalike_similarity(a: str, b: str) -> float:
    from difflib import SequenceMatcher

    return SequenceMatcher(None, a, b).ratio()


def analyze_headers(
    from_address: str | None,
    from_display_name: str | None,
    reply_to: str | None,
    return_path: str | None,
    subject: str | None,
    body_text: str | None,
) -> list[HeaderFinding]:
    findings: list[HeaderFinding] = []

    from_domain = _domain_of(from_address)
    reply_domain = _domain_of(reply_to)
    return_domain = _domain_of(return_path)

    # Identity mismatch: Reply-To differs from From
    if reply_to and from_address and reply_to.lower() != from_address.lower():
        findings.append(
            HeaderFinding(
                rule_id="IDENTITY-REPLY-TO-MISMATCH-001",
                category="IDENTITY",
                severity="high",
                title="Reply-To address does not match From address",
                description=f"From: {from_address}, Reply-To: {reply_to}",
                evidence={"from": from_address, "reply_to": reply_to},
                score_delta=18,
                confidence=0.9,
            )
        )

    # Return-Path mismatch
    if return_domain and from_domain and return_domain != from_domain:
        findings.append(
            HeaderFinding(
                rule_id="IDENTITY-RETURN-PATH-MISMATCH-001",
                category="IDENTITY",
                severity="medium",
                title="Return-Path domain does not match From domain",
                description=f"From domain: {from_domain}, Return-Path domain: {return_domain}",
                evidence={"from_domain": from_domain, "return_path_domain": return_domain},
                score_delta=10,
                confidence=0.8,
            )
        )

    # Executive display name spoofing
    if _display_suspicious(from_display_name):
        findings.append(
            HeaderFinding(
                rule_id="IDENTITY-EXECUTIVE-DISPLAY-NAME-001",
                category="IDENTITY",
                severity="medium",
                title="Sender display name contains executive/authority terms",
                description=f"Display name: {from_display_name}",
                evidence={"display_name": from_display_name},
                score_delta=8,
                confidence=0.7,
            )
        )

    # Lookalike domain heuristic
    if from_domain and reply_domain and from_domain != reply_domain:
        sim = _lookalike_similarity(from_domain, reply_domain)
        if sim > 0.7:
            findings.append(
                HeaderFinding(
                    rule_id="IDENTITY-LOOKALIKE-DOMAIN-001",
                    category="IDENTITY",
                    severity="high",
                    title="Possible lookalike domain in Reply-To",
                    description=f"From domain {from_domain} is similar to Reply-To domain {reply_domain}",
                    evidence={"from_domain": from_domain, "reply_domain": reply_domain, "similarity": sim},
                    score_delta=15,
                    confidence=round(sim, 2),
                )
            )

    # Subject urgency / pressure
    if subject:
        lower = subject.lower()
        urgency_words = ["urgent", "immediate", "asap", "action required", "expires", "suspend"]
        if any(w in lower for w in urgency_words):
            findings.append(
                HeaderFinding(
                    rule_id="CONTENT-URGENCY-001",
                    category="CONTENT",
                    severity="low",
                    title="Subject contains urgency or pressure language",
                    description=f"Subject: {subject}",
                    evidence={"subject": subject},
                    score_delta=5,
                    confidence=0.7,
                )
            )

    # Body financial pressure
    if body_text:
        lower = body_text.lower()
        financial_terms = ["wire transfer", "payment", "invoice", "bank account", "swift"]
        if any(t in lower for t in financial_terms):
            findings.append(
                HeaderFinding(
                    rule_id="CONTENT-FINANCIAL-001",
                    category="CONTENT",
                    severity="medium",
                    title="Body references financial transfer or payment",
                    description="Email body contains financial transaction language.",
                    evidence={"terms_found": [t for t in financial_terms if t in lower]},
                    score_delta=10,
                    confidence=0.8,
                )
            )

    return findings
