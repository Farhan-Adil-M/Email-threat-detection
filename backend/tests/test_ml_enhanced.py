"""Tests for enhanced ML baseline features."""
from app.services.ml_baseline import classify_email


def test_urgency_features_increase_phishing_prob():
    """Email with urgency words gets higher phishing probability."""
    result = classify_email(
        subject="Your account will be suspended immediately",
        body="Verify your identity or lose access forever",
        from_address="security@account-verify.com",
        reply_to=None,
    )
    assert result.phishing_probability > 0.2
    assert result.model_version == "nb-baseline-002"


def test_wire_transfer_features_increase_bec_prob():
    """Email with wire transfer language gets higher BEC probability."""
    result = classify_email(
        subject="Urgent: Wire transfer needed",
        body="Please wire $50,000 to the following bank account immediately",
        from_address="ceo@acme-corp.com",
        reply_to=None,
    )
    assert result.bec_probability > 0.2


def test_reply_to_mismatch_boosts_impersonation():
    """Reply-To mismatch boosts impersonation probability."""
    result = classify_email(
        subject="Confidential request",
        body="Please handle this immediately",
        from_address="ceo@acme-corp.com",
        reply_to="ceo.personal@gmail.com",
    )
    assert result.impersonation_probability > 0.1


def test_legitimate_email_gets_low_scores():
    """Benign email gets low probabilities across all categories."""
    result = classify_email(
        subject="Team standup notes",
        body="Here are the meeting notes from today's standup",
        from_address="sarah@company.com",
        reply_to=None,
    )
    total = result.phishing_probability + result.bec_probability + result.impersonation_probability
    assert total < 0.8


def test_model_version_updated():
    """Model version is nb-baseline-002."""
    result = classify_email("test", "test", None, None)
    assert result.model_version == "nb-baseline-002"


def test_result_has_limitations():
    """MLResult includes limitations list."""
    result = classify_email("test", "test", None, None)
    assert len(result.limitations) > 0
    assert any("demo baseline" in l.lower() for l in result.limitations)


def test_important_features_are_sorted():
    """Important features are sorted by impact descending."""
    result = classify_email("urgent wire transfer", "ceo request", None, None)
    if len(result.important_features) > 1:
        impacts = [f["impact"] for f in result.important_features]
        assert impacts == sorted(impacts, reverse=True)


def test_result_has_three_probabilities():
    """MLResult has phishing, bec, and impersonation probabilities."""
    result = classify_email("test", "test", None, None)
    assert 0 <= result.phishing_probability <= 1
    assert 0 <= result.bec_probability <= 1
    assert 0 <= result.impersonation_probability <= 1


def test_structured_signals_detect_urgency():
    """Structured signals detect urgency keywords."""
    from app.services.ml_baseline import _structured_signals
    signals = _structured_signals("URGENT: Account suspended", "Verify immediately", None, None)
    assert signals["urgency"] > 0


def test_structured_signals_detect_payment():
    """Structured signals detect payment-related keywords."""
    from app.services.ml_baseline import _structured_signals
    signals = _structured_signals("Wire transfer", "Please wire funds to bank account", None, None)
    assert signals["payment_request"] > 0
