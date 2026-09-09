import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuthRecord:
    mechanism: str  # SPF, DKIM, DMARC
    domain: str | None = None
    result: str | None = None
    alignment: str | None = None
    policy: str | None = None
    explanation: str | None = None
    raw_result: str | None = None


def _normalize_result(value: str) -> str:
    value = value.lower()
    if value in ("pass", "fail", "neutral", "none", "softfail", "temperror", "permerror"):
        return value
    return value


def parse_authentication_results(header_values: list[str]) -> list[AuthRecord]:
    """Parse Authentication-Results header values.

    Example header:
    Authentication-Results: mx.google.com;
        spf=pass smtp.mailfrom=example.com;
        dkim=pass header.i=@example.com;
        dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=example.com
    """
    records: list[AuthRecord] = []
    if not header_values:
        return records

    for raw in header_values:
        # Split on semicolons, but the first token is usually the authserv-id.
        parts = [p.strip() for p in raw.split(";")]
        for part in parts[1:]:
            if not part:
                continue
            # Mechanism is the first word before '='
            mech_match = re.match(r"^(spf|dkim|dmarc)\s*=\s*(\S+)", part, re.IGNORECASE)
            if not mech_match:
                continue
            mechanism = mech_match.group(1).upper()
            result = _normalize_result(mech_match.group(2))

            record = AuthRecord(
                mechanism=mechanism,
                result=result,
                raw_result=part,
            )

            # Extract domain-ish fields
            if mechanism == "SPF":
                m = re.search(r"smtp\.mailfrom=([^\s;]+)", part, re.IGNORECASE)
                if m:
                    record.domain = m.group(1).strip()
            elif mechanism == "DKIM":
                m = re.search(r"header\.i=@?([^\s;]+)", part, re.IGNORECASE)
                if m:
                    record.domain = m.group(1).strip()
                # DKIM alignment may appear as adkim= or just result
            elif mechanism == "DMARC":
                m = re.search(r"header\.from=([^\s;]+)", part, re.IGNORECASE)
                if m:
                    record.domain = m.group(1).strip()
                p = re.search(r"\bp=(\S+)", part, re.IGNORECASE)
                if p:
                    record.policy = p.group(1).strip().upper()
                # Alignment may appear as aspf= / adkim= inside parentheses
                a = re.search(r"aspf=(\S+)", part, re.IGNORECASE)
                if a:
                    record.alignment = a.group(1).strip().lower()

            # Generic alignment extraction
            if not record.alignment:
                a = re.search(r"(?:adkim|aspf|alignment)=(\S+)", part, re.IGNORECASE)
                if a:
                    record.alignment = a.group(1).strip().lower()

            # Extract parenthetical explanation
            paren = re.search(r"\(([^)]*)\)", part)
            if paren:
                record.explanation = paren.group(1).strip()

            records.append(record)

    return records


def summarize_auth_results(records: list[AuthRecord]) -> dict[str, Any]:
    """Return a simple summary of authentication results."""
    summary: dict[str, Any] = {"spf": None, "dkim": None, "dmarc": None}
    for record in records:
        key = record.mechanism.lower()
        if key in summary:
            summary[key] = {
                "result": record.result,
                "domain": record.domain,
                "alignment": record.alignment,
                "policy": record.policy,
            }
    return summary
