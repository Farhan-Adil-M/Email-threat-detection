from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class NormalizedIntelResult:
    provider: str
    status: str
    indicator: str
    indicator_type: str
    data: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    source_reference: str | None = None
    raw_available: bool = False
    queried_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class IntelligenceProvider:
    name = "provider"

    def lookup(self, indicator: str, indicator_type: str) -> NormalizedIntelResult:
        raise NotImplementedError
