"""Diagnosis service - orchestrates ML-based fault detection."""

import logging
from app.schemas.diagnosis import DiagnosisRequest, DiagnosisResult
from app.ml.predict import predict_fault

logger = logging.getLogger(__name__)


class DiagnosisService:
    """Thin orchestration layer between the API and the ML predictor.

    The service is responsible for:
    - Preprocessing the telemetry before sending it to the model.
    - Storing diagnosis results.
    - Returning structured DiagnosisResult objects.
    """

    def __init__(self) -> None:
        self._history: list[DiagnosisResult] = []

    async def diagnose(self, request: DiagnosisRequest) -> DiagnosisResult:
        """Run fault diagnosis and return the result."""
        result = predict_fault(request.telemetry)
        self._history.append(result)
        logger.info("Diagnosis complete: fault=%s confidence=%.2f", result.fault_label, result.confidence)
        return result

    async def get_history(self) -> list[DiagnosisResult]:
        """Return recent diagnosis results."""
        return self._history[-20:]  # last 20 entries
