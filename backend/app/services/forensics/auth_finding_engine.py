from dataclasses import dataclass, field
from typing import Any

from app.services.forensics.header_analyzer import HeaderFinding


@dataclass
class AuthSummary:
    spf_result: str | None = None
    spf_domain: str | None = None
    dkim_result: str | None = None
    dkim_domain: str | None = None
    dmarc_result: str | None = None
    dmarc_domain: str | None = None
    dmarc_policy: str | None = None
    dmarc_alignment: str | None = None


def _result_is_fail(value: str | None) -> bool:
    if not value:
        return False
    return value.lower() in ("fail", "permerror", "temperror")


def _result_is_pass(value: str | None) -> bool:
    if not value:
        return False
    return value.lower() == "pass"


def _explain_auth_result(mechanism: str, result: str | None, domain: str | None) -> str:
    base = f"{mechanism} result"
    if result:
        base += f": {result.upper()}"
    if domain:
        base += f" for domain {domain}"
    if result and result.lower() == "none":
        base += ". No authentication record was found."
    elif result and result.lower() == "neutral":
        base += ". Sender published a neutral policy."
    elif result and result.lower() == "softfail":
        base += ". Sender policy recommends but does not require rejection."
    elif _result_is_fail(result):
        base += ". This means the message did not pass authentication checks."
    elif _result_is_pass(result):
        base += ". The message passed this authentication mechanism."
    return base


def generate_auth_findings(
    from_domain: str | None,
    auth_records: list[Any],
) -> list[HeaderFinding]:
    """Generate findings from parsed Authentication-Results records.

    `auth_records` should be objects with attributes: mechanism, result, domain,
    alignment, policy.
    """
    findings: list[HeaderFinding] = []
    summary = AuthSummary()

    for record in auth_records:
        mech = record.mechanism.upper()
        result = (record.result or "").lower()
        domain = record.domain

        if mech == "SPF":
            summary.spf_result = result
            summary.spf_domain = domain
        elif mech == "DKIM":
            summary.dkim_result = result
            summary.dkim_domain = domain
        elif mech == "DMARC":
            summary.dmarc_result = result
            summary.dmarc_domain = domain
            summary.dmarc_policy = (record.policy or "").upper() or None
            summary.dmarc_alignment = record.alignment

    # Missing auth results entirely
    if not auth_records:
        findings.append(
            HeaderFinding(
                rule_id="AUTH-MISSING-001",
                category="AUTHENTICATION",
                severity="medium",
                title="No Authentication-Results header present",
                description="The message contains no Authentication-Results header. SPF, DKIM, and DMARC results are unavailable.",
                evidence={"from_domain": from_domain},
                score_delta=12,
                confidence=0.9,
            )
        )
        return findings

    # SPF findings
    if summary.spf_result is None:
        findings.append(
            HeaderFinding(
                rule_id="AUTH-SPF-MISSING-001",
                category="AUTHENTICATION",
                severity="low",
                title="SPF result not present in Authentication-Results",
                description="The receiving server did not publish an SPF result for this message.",
                evidence={"from_domain": from_domain},
                score_delta=5,
                confidence=0.7,
            )
        )
    elif _result_is_fail(summary.spf_result):
        findings.append(
            HeaderFinding(
                rule_id="AUTH-SPF-FAIL-001",
                category="AUTHENTICATION",
                severity="high",
                title="SPF authentication failed",
                description=_explain_auth_result("SPF", summary.spf_result, summary.spf_domain),
                evidence={
                    "spf_result": summary.spf_result,
                    "spf_domain": summary.spf_domain,
                    "from_domain": from_domain,
                },
                score_delta=20,
                confidence=0.85,
            )
        )

    # DKIM findings
    if summary.dkim_result is None:
        findings.append(
            HeaderFinding(
                rule_id="AUTH-DKIM-MISSING-001",
                category="AUTHENTICATION",
                severity="low",
                title="DKIM result not present in Authentication-Results",
                description="The receiving server did not publish a DKIM result for this message.",
                evidence={"from_domain": from_domain},
                score_delta=5,
                confidence=0.7,
            )
        )
    elif _result_is_fail(summary.dkim_result):
        findings.append(
            HeaderFinding(
                rule_id="AUTH-DKIM-FAIL-001",
                category="AUTHENTICATION",
                severity="high",
                title="DKIM authentication failed",
                description=_explain_auth_result("DKIM", summary.dkim_result, summary.dkim_domain),
                evidence={
                    "dkim_result": summary.dkim_result,
                    "dkim_domain": summary.dkim_domain,
                    "from_domain": from_domain,
                },
                score_delta=20,
                confidence=0.85,
            )
        )

    # DMARC findings
    if summary.dmarc_result is None:
        findings.append(
            HeaderFinding(
                rule_id="AUTH-DMARC-MISSING-001",
                category="AUTHENTICATION",
                severity="medium",
                title="DMARC result not present in Authentication-Results",
                description="The receiving server did not publish a DMARC result for this message.",
                evidence={"from_domain": from_domain},
                score_delta=10,
                confidence=0.75,
            )
        )
    elif _result_is_fail(summary.dmarc_result):
        policy_note = ""
        if summary.dmarc_policy:
            policy_note = f" DMARC policy is {summary.dmarc_policy}."
        findings.append(
            HeaderFinding(
                rule_id="AUTH-DMARC-FAIL-001",
                category="AUTHENTICATION",
                severity="high",
                title="DMARC authentication failed",
                description=_explain_auth_result("DMARC", summary.dmarc_result, summary.dmarc_domain) + policy_note,
                evidence={
                    "dmarc_result": summary.dmarc_result,
                    "dmarc_domain": summary.dmarc_domain,
                    "dmarc_policy": summary.dmarc_policy,
                    "dmarc_alignment": summary.dmarc_alignment,
                    "from_domain": from_domain,
                },
                score_delta=25,
                confidence=0.88,
            )
        )
    elif summary.dmarc_result == "none":
        findings.append(
            HeaderFinding(
                rule_id="AUTH-DMARC-NONE-001",
                category="AUTHENTICATION",
                severity="informational",
                title="DMARC policy is none",
                description="The sender domain has a DMARC record but policy is p=none; failed authentication would not cause rejection.",
                evidence={
                    "dmarc_result": summary.dmarc_result,
                    "dmarc_domain": summary.dmarc_domain,
                    "dmarc_policy": summary.dmarc_policy,
                },
                score_delta=2,
                confidence=0.8,
            )
        )

    # Alignment finding
    if summary.dmarc_alignment and summary.dmarc_alignment.lower() == "r":
        findings.append(
            HeaderFinding(
                rule_id="AUTH-DMARC-RELAXED-ALIGNMENT-001",
                category="AUTHENTICATION",
                severity="informational",
                title="DMARC uses relaxed alignment",
                description="Relaxed alignment allows subdomains to satisfy alignment. Stricter senders use strict alignment.",
                evidence={"dmarc_alignment": summary.dmarc_alignment},
                score_delta=1,
                confidence=0.7,
            )
        )

    return findings
