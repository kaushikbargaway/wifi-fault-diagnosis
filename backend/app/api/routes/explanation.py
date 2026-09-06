"""RAG / LLM explanation endpoints."""

from fastapi import APIRouter, Depends
from app.schemas.diagnosis import DiagnosisResult
from app.services.explanation_service import ExplanationService
from app.api.dependencies import get_explanation_service

router = APIRouter(prefix="/explanation")


@router.post("/")
async def explain(
    diagnosis: DiagnosisResult,
    svc: ExplanationService = Depends(get_explanation_service),
) -> dict:
    """Generate a human-readable explanation for the given diagnosis."""
    return await svc.explain(diagnosis)
