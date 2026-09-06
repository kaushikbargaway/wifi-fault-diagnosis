"""Fault diagnosis endpoints."""

from fastapi import APIRouter, Depends
from app.schemas.diagnosis import DiagnosisRequest, DiagnosisResult
from app.services.diagnosis_service import DiagnosisService
from app.api.dependencies import get_diagnosis_service

router = APIRouter(prefix="/diagnosis")


@router.post("/", response_model=DiagnosisResult)
async def diagnose(
    request: DiagnosisRequest,
    svc: DiagnosisService = Depends(get_diagnosis_service),
) -> DiagnosisResult:
    """Run fault diagnosis on the supplied telemetry."""
    return await svc.diagnose(request)


@router.get("/history")
async def get_diagnosis_history(
    svc: DiagnosisService = Depends(get_diagnosis_service),
) -> list:
    """Return recent diagnosis history."""
    return await svc.get_history()
