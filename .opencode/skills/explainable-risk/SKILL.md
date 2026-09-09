---
name: explainable-risk
description: Use when computing risk scores, fusing deterministic findings with ML, or rendering analyst-readable reasoning. Every score must have a reproducible contribution breakdown.
---

# Skill: Explainable Risk

## Purpose

- Deterministic findings
- Score contributions
- ML fusion
- Calibrated confidence
- Analyst-readable reasoning

## Rules

- Every important score has structured evidence.
- Never let LLM prose modify scores.
- Scores must be reproducible from the same email, configuration, fixtures, and model version.
- Distinguish risk (how suspicious) from confidence (how strongly evidence supports it).

## Risk scale

```text
0–19   LOW
20–39  GUARDED
40–59  MEDIUM
60–79  HIGH
80–100 CRITICAL
```

Thresholds can change during calibration.

## Risk assessment contract

```json
{
  "risk_score": 88,
  "risk_level": "high",
  "confidence": 0.82,
  "classification": ["phishing", "impersonation"],
  "model_version": "baseline-001",
  "contributions": [],
  "limitations": []
}
```

## Contribution example

```text
+25 DMARC alignment failure
+18 sender/reply-to identity mismatch
+15 lookalike domain
+12 BEC language
+08 suspicious infrastructure
+07 URL risk
+06 ML contribution
```

Numbers are illustrative; calibrate with real fixtures.

## Degraded behavior

If ML is unavailable, fall back to deterministic score.
If intelligence is unavailable, continue and note the limitation.
