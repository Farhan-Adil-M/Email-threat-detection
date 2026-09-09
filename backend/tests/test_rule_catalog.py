from app.services.rule_catalog import RULE_CATALOG, RULE_VERSION, get_rule


def test_rule_catalog_has_versioned_definitions():
    assert RULE_VERSION
    assert len(RULE_CATALOG) >= 20
    for rule_id, rule in RULE_CATALOG.items():
        assert rule_id == rule.rule_id
        assert rule.description
        assert rule.evidence_requirements
        assert rule.mitigation


def test_known_url_rule_is_catalogued():
    rule = get_rule("URL-USERINFO-001")
    assert rule is not None
    assert rule.category == "URL"
    assert rule.score_contribution == 15
