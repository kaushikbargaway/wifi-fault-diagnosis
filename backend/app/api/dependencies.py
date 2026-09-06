"""FastAPI dependency injection helpers.

Each `get_*` function acts as a factory so that services can be swapped
during testing without modifying route files.
"""

from app.services.telemetry_service import TelemetryService
from app.services.diagnosis_service import DiagnosisService
from app.services.recovery_service import RecoveryService
from app.services.digital_twin_service import DigitalTwinService
from app.services.explanation_service import ExplanationService


def get_telemetry_service() -> TelemetryService:
    return TelemetryService()


def get_diagnosis_service() -> DiagnosisService:
    return DiagnosisService()


def get_recovery_service() -> RecoveryService:
    return RecoveryService()


def get_digital_twin_service() -> DigitalTwinService:
    return DigitalTwinService()


def get_explanation_service() -> ExplanationService:
    return ExplanationService()
