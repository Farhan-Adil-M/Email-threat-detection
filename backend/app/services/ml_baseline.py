import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any


MODEL_VERSION = "nb-baseline-002"
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9._-]{1,31}", re.IGNORECASE)


@dataclass
class MLResult:
    phishing_probability: float
    bec_probability: float
    impersonation_probability: float
    important_features: list[dict[str, Any]]
    limitations: list[str]
    model_version: str = MODEL_VERSION


# Synthetic seed corpus — intentionally tiny. Demo baseline, not an evaluated model.
TRAINING = [
    ("legitimate quarterly report normal meeting update", "legitimate"),
    ("team schedule document requested review ordinary message", "legitimate"),
    ("monthly newsletter product update announcement", "legitimate"),
    ("calendar invitation meeting tomorrow afternoon", "legitimate"),
    ("urgent wire transfer confidential payment bank account", "bec"),
    ("ceo executive request immediate invoice transfer", "bec"),
    ("confidential wire transfer acquisition board approval", "bec"),
    ("vendor payment change banking details urgent", "bec"),
    ("verify account login password suspended click portal", "phishing"),
    ("security alert credential login reset account", "phishing"),
    ("account suspended verify identity immediately urgent", "phishing"),
    ("unusual sign-in activity confirm your account", "phishing"),
    ("ceo cfo president impersonation reply to mismatch", "impersonation"),
    ("executive authority urgent secret request", "impersonation"),
    ("ceo wire transfer impersonation wire payment", "impersonation"),
    ("director urgent request confidential wire payment", "impersonation"),
]

# Structured signal patterns for feature-level boosting
URGENCY_WORDS = {"urgent", "immediately", "suspended", "verify", "confirm", "alert", "action", "required", "expire", "expires", "deadline"}
CREDENTIAL_WORDS = {"password", "credential", "login", "signin", "sign-in", "verify", "identity", "account", "confirm", "reset", "update"}
PAYMENT_WORDS = {"wire", "transfer", "payment", "invoice", "bank", "account", "routing", "beneficiary", "financial", "confidential"}
EXECUTIVE_WORDS = {"ceo", "cfo", "cto", "president", "director", "executive", "urgent", "confidential", "secret"}


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "")]


def _structured_signals(subject: str | None, body: str | None, from_address: str | None, reply_to: str | None) -> dict[str, float]:
    text = " ".join(v or "" for v in (subject, body)).lower()
    tokens = set(_tokens(text))
    signals: dict[str, float] = {}
    signals["urgency"] = len(tokens & URGENCY_WORDS) / max(len(URGENCY_WORDS), 1)
    signals["credential_request"] = len(tokens & CREDENTIAL_WORDS) / max(len(CREDENTIAL_WORDS), 1)
    signals["payment_request"] = len(tokens & PAYMENT_WORDS) / max(len(PAYMENT_WORDS), 1)
    signals["executive_terms"] = len(tokens & EXECUTIVE_WORDS) / max(len(EXECUTIVE_WORDS), 1)
    if from_address and reply_to:
        from_domain = from_address.rsplit("@", 1)[-1].lower() if "@" in from_address else ""
        reply_domain = reply_to.rsplit("@", 1)[-1].lower() if "@" in reply_to else ""
        signals["reply_to_mismatch"] = 1.0 if from_domain and reply_domain and from_domain != reply_domain else 0.0
    else:
        signals["reply_to_mismatch"] = 0.0
    return signals


def _log_probabilities(tokens: list[str]) -> dict[str, float]:
    classes = sorted({label for _, label in TRAINING})
    class_docs = Counter(label for _, label in TRAINING)
    word_counts: dict[str, Counter[str]] = defaultdict(Counter)
    totals: Counter[str] = Counter()
    vocabulary: set[str] = set()
    for text, label in TRAINING:
        words = _tokens(text)
        word_counts[label].update(words)
        totals[label] += len(words)
        vocabulary.update(words)
    scores: dict[str, float] = {}
    for label in classes:
        score = math.log(class_docs[label] / len(TRAINING))
        denominator = totals[label] + len(vocabulary)
        for token in tokens:
            score += math.log((word_counts[label][token] + 1) / denominator)
        scores[label] = score
    maximum = max(scores.values())
    normalizer = sum(math.exp(value - maximum) for value in scores.values())
    return {label: math.exp(value - maximum) / normalizer for label, value in scores.items()}


def classify_email(subject: str | None, body: str | None, from_address: str | None, reply_to: str | None) -> MLResult:
    text = " ".join(value or "" for value in (subject, body, from_address, reply_to))
    tokens = _tokens(text)
    probabilities = _log_probabilities(tokens)
    signals = _structured_signals(subject, body, from_address, reply_to)

    boosted = dict(probabilities)
    if signals["reply_to_mismatch"] > 0:
        boosted["impersonation"] = boosted.get("impersonation", 0) + 0.08
        boosted["bec"] = boosted.get("bec", 0) + 0.04
    if signals["payment_request"] > 0.1:
        boosted["bec"] = boosted.get("bec", 0) + signals["payment_request"] * 0.06
    if signals["credential_request"] > 0.1:
        boosted["phishing"] = boosted.get("phishing", 0) + signals["credential_request"] * 0.05
    if signals["executive_terms"] > 0.05:
        boosted["impersonation"] = boosted.get("impersonation", 0) + signals["executive_terms"] * 0.04

    total = sum(boosted.values())
    if total > 0:
        boosted = {k: v / total for k, v in boosted.items()}

    important = []
    for token in sorted(set(tokens)):
        token_probs = _log_probabilities([token])
        impact = max(token_probs.values()) - min(token_probs.values())
        if impact > 0.05:
            important.append({"feature": token, "impact": round(impact, 4)})
    important.sort(key=lambda item: item["impact"], reverse=True)

    return MLResult(
        phishing_probability=round(boosted.get("phishing", 0.0), 4),
        bec_probability=round(boosted.get("bec", 0.0), 4),
        impersonation_probability=round(boosted.get("impersonation", 0.0), 4),
        important_features=important[:10],
        limitations=[
            "This is a demo baseline classifier trained on a tiny synthetic seed corpus.",
            "It has not been evaluated on real-world phishing datasets.",
            "Do not rely on it for production decisions.",
            "Probabilities are model signals, not forensic facts or measured performance.",
        ],
    )
