from dataclasses import dataclass


RULE_VERSION = "rules-001"


@dataclass(frozen=True)
class RuleDefinition:
    rule_id: str
    category: str
    name: str
    description: str
    default_severity: str
    score_contribution: int
    evidence_requirements: tuple[str, ...]
    mitigation: str


def _rule(rule_id: str, category: str, name: str, description: str, severity: str, score: int, evidence: tuple[str, ...], mitigation: str) -> RuleDefinition:
    return RuleDefinition(rule_id, category, name, description, severity, score, evidence, mitigation)


RULE_CATALOG: dict[str, RuleDefinition] = {
    rule.rule_id: rule
    for rule in (
        _rule("IDENTITY-REPLY-TO-MISMATCH-001", "IDENTITY", "Reply-To mismatch", "Reply-To differs from From.", "high", 18, ("From", "Reply-To"), "Verify the sender through an independent channel."),
        _rule("IDENTITY-RETURN-PATH-MISMATCH-001", "IDENTITY", "Return-Path mismatch", "Return-Path domain differs from From domain.", "medium", 10, ("From", "Return-Path"), "Review the sending path and authentication results."),
        _rule("IDENTITY-EXECUTIVE-DISPLAY-NAME-001", "IDENTITY", "Executive display name", "Display name contains authority terms.", "medium", 8, ("From display name",), "Do not rely on display name alone."),
        _rule("IDENTITY-LOOKALIKE-DOMAIN-001", "IDENTITY", "Lookalike domain", "Related identity domains are highly similar.", "high", 15, ("From domain", "Reply-To domain"), "Compare the domain with an approved organization baseline."),
        _rule("CONTENT-URGENCY-001", "CONTENT", "Urgency language", "Subject contains pressure or urgency language.", "low", 5, ("Subject",), "Use an independent verification step before acting."),
        _rule("CONTENT-FINANCIAL-001", "CONTENT", "Financial language", "Body contains payment or transfer language.", "medium", 10, ("Body text",), "Verify payment instructions out of band."),
        _rule("AUTH-MISSING-001", "AUTHENTICATION", "Missing authentication results", "No Authentication-Results header was available.", "medium", 12, ("Authentication-Results absence",), "Treat authentication as unknown, not as proof of maliciousness."),
        _rule("AUTH-SPF-MISSING-001", "AUTHENTICATION", "Missing SPF result", "No SPF result was published in the available results.", "low", 5, ("Authentication-Results",), "Record the limitation and inspect other evidence."),
        _rule("AUTH-SPF-FAIL-001", "AUTHENTICATION", "SPF failure", "SPF did not authenticate the envelope sender.", "high", 20, ("SPF result",), "Treat as evidence requiring corroboration."),
        _rule("AUTH-DKIM-MISSING-001", "AUTHENTICATION", "Missing DKIM result", "No DKIM result was published in the available results.", "low", 5, ("Authentication-Results",), "Record the limitation and inspect other evidence."),
        _rule("AUTH-DKIM-FAIL-001", "AUTHENTICATION", "DKIM failure", "DKIM did not authenticate the message signature.", "high", 20, ("DKIM result",), "Treat as evidence requiring corroboration."),
        _rule("AUTH-DMARC-MISSING-001", "AUTHENTICATION", "Missing DMARC result", "No DMARC result was published in the available results.", "medium", 10, ("Authentication-Results",), "Record the limitation and inspect other evidence."),
        _rule("AUTH-DMARC-FAIL-001", "AUTHENTICATION", "DMARC failure", "DMARC alignment/authentication failed.", "high", 25, ("DMARC result",), "DMARC failure is evidence, not proof of maliciousness."),
        _rule("AUTH-DMARC-NONE-001", "AUTHENTICATION", "DMARC none policy", "The sender policy is monitoring-only.", "informational", 2, ("DMARC policy",), "Do not treat p=none as a pass or fail by itself."),
        _rule("AUTH-DMARC-RELAXED-ALIGNMENT-001", "AUTHENTICATION", "Relaxed DMARC alignment", "DMARC uses relaxed alignment.", "informational", 1, ("DMARC alignment",), "Interpret alignment alongside the full authentication context."),
        _rule("URL-MALFORMED-001", "URL", "Malformed URL", "URL could not be parsed safely.", "medium", 8, ("Extracted URL",), "Do not fetch the URL automatically."),
        _rule("URL-UNUSUAL-SCHEME-001", "URL", "Unusual URL scheme", "URL uses a non-standard web scheme.", "medium", 10, ("URL scheme",), "Inspect the URL without active fetching."),
        _rule("URL-USERINFO-001", "URL", "URL userinfo", "URL contains embedded user information.", "high", 15, ("URL",), "Display the true hostname prominently."),
        _rule("URL-IP-LITERAL-001", "URL", "IP literal URL", "URL uses an IP literal rather than a domain.", "high", 12, ("URL hostname",), "Treat as an indicator requiring corroboration."),
        _rule("URL-PUNYCODE-001", "URL", "Punycode hostname", "URL contains an internationalized hostname representation.", "medium", 8, ("URL hostname",), "Review for homograph/lookalike abuse."),
        _rule("URL-UNUSUAL-PORT-001", "URL", "Unusual URL port", "URL uses a non-standard web port.", "medium", 8, ("URL port",), "Do not fetch without explicit safe-scan controls."),
        _rule("URL-DEEP-HOSTNAME-001", "URL", "Deep hostname", "URL hostname has unusually deep nesting.", "low", 4, ("URL hostname",), "Compare the registrable domain with trusted domains."),
    )
}


def get_rule(rule_id: str) -> RuleDefinition | None:
    return RULE_CATALOG.get(rule_id)
