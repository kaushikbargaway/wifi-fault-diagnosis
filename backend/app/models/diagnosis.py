"""ORM model for diagnosis results (placeholder)."""

from datetime import datetime
from typing import Optional


class DiagnosisRecord:
    """Persisted result of a fault diagnosis run."""

    id: int
    timestamp: datetime
    telemetry_id: Optional[int]  # FK to TelemetryRecord
    fault_label: str
    confidence: float  # 0.0 - 1.0
    raw_probabilities: dict  # label -> probability
