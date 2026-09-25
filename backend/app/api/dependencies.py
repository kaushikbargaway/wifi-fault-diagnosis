"""
FastAPI dependency injection helpers.
Services that need database access receive a DB session via Depends(get_db).
"""

from sqlalchemy.orm import Session
from fastapi import Depends

from app.database.connection import get_db
from app.services.telemetry_service import TelemetryService
from app.services.diagnosis_service import DiagnosisService
from app.services.recovery_service import RecoveryService
from app.services.digital_twin_service import DigitalTwinService
from app.services.explanation_service import ExplanationService


def get_telemetry_service(db: Session = Depends(get_db)) -> TelemetryService:
    return TelemetryService(db)


def get_diagnosis_service(db: Session = Depends(get_db)) -> DiagnosisService:
    return DiagnosisService(db)


def get_recovery_service() -> RecoveryService:
    return RecoveryService()


def get_digital_twin_service() -> DigitalTwinService:
    return DigitalTwinService()


def get_explanation_service() -> ExplanationService:
    return ExplanationService()
