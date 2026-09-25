"""Diagnosis service — orchestrates ML-based fault detection with DB persistence."""

import logging
from sqlalchemy.orm import Session

from app.schemas.diagnosis import DiagnosisRequest, DiagnosisResult
from app.schemas.telemetry import TelemetryCreate
from app.ml.predict import predict_fault
from app.database.repositories import DiagnosisRepository, TelemetryRepository

logger = logging.getLogger(__name__)


class DiagnosisService:
    """Runs ML fault diagnosis and persists results to SQLite."""

    def __init__(self, db: Session) -> None:
        self.diagnosis_repo = DiagnosisRepository(db)
        self.telemetry_repo = TelemetryRepository(db)

    async def diagnose(self, request: DiagnosisRequest) -> DiagnosisResult:
        """Run fault diagnosis, persist result, return DiagnosisResult."""
        # 1. Run ML prediction
        result = predict_fault(request.telemetry)

        # 2. Persist to database
        self.diagnosis_repo.save({
            "fault_label":   result.fault_label,
            "confidence":    result.confidence,
            "probabilities": result.probabilities,
            "timestamp":     result.timestamp,
        })

        # 3. Update fault label on the matching telemetry record (if stored)
        latest = self.telemetry_repo.get_latest()
        if latest and latest.device_id == (request.telemetry.device_id or ""):
            self.telemetry_repo.update_fault_label(latest.id, result.fault_label)

        logger.info(
            "Diagnosis complete: fault=%s confidence=%.2f",
            result.fault_label,
            result.confidence,
        )
        return result

    async def get_history(self, limit: int = 20) -> list[dict]:
        """Return recent diagnosis records from the database."""
        records = self.diagnosis_repo.get_history(limit=limit)
        return [r.to_dict() for r in records]

    async def get_fault_counts(self) -> dict[str, int]:
        """Return how many times each fault type has been diagnosed."""
        return self.diagnosis_repo.fault_counts()

    async def get_count(self) -> int:
        """Return total number of diagnoses performed."""
        return self.diagnosis_repo.count()
