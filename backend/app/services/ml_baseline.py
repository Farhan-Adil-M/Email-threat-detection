import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any


MODEL_VERSION = "nb-baseline-001"
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9._-]{1,31}", re.IGNORECASE)


@dataclass
class MLResult:
    phishing_probability: float
    bec_probability: float
    impersonation_probability: float
    important_features: list[dict[str, Any]]
    limitations: list[str]
    model_version: str = MODEL_VERSION


# Synthetic, intentionally tiny seed corpus. It is a demo baseline, not an evaluation dataset.
TRAINING = [
    ("legitimate quarterly report normal meeting update", "legitimate"),
    ("team schedule document requested review ordinary message", "legitimate"),
    ("urgent wire transfer confidential payment bank account", "bec"),
    ("ceo executive request immediate invoice transfer", "bec"),
    ("verify account login password suspended click portal", "phishing"),
    ("security alert credential login reset account", "phishing"),
    ("ceo cfo president impersonation reply to mismatch", "impersonation"),
    ("executive authority urgent secret request", "impersonation"),
]


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "")]


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
    important = []
    for token in sorted(set(tokens)):
        token_probs = _log_probabilities([token])
        impact = max(token_probs.values()) - min(token_probs.values())
        if impact > 0.05:
            important.append({"feature": token, "impact": round(impact, 4)})
    important.sort(key=lambda item: item["impact"], reverse=True)
    return MLResult(
        phishing_probability=round(probabilities.get("phishing", 0.0), 4),
        bec_probability=round(probabilities.get("bec", 0.0), 4),
        impersonation_probability=round(probabilities.get("impersonation", 0.0), 4),
        important_features=important[:10],
        limitations=[
            "Baseline trained on a tiny synthetic seed corpus.",
            "Probabilities are model signals, not forensic facts or measured performance.",
        ],
    )
