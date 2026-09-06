"""ORM model for recovery recommendations (placeholder)."""

from datetime import datetime
from typing import List


class RecoveryRecord:
    """Persisted recovery recommendation linked to a diagnosis."""

    id: int
    timestamp: datetime
    diagnosis_id: int  # FK to DiagnosisRecord
    recommended_actions: List[str]
