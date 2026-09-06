"""Recovery recommendation endpoints."""

from fastapi import APIRouter, Depends
from app.schemas.recovery import RecoveryRequest, RecoveryPlan
from app.services.recovery_service import RecoveryService
from app.api.dependencies import get_recovery_service

router = APIRouter(prefix="/recovery")


@router.post("/recommend", response_model=RecoveryPlan)
async def recommend(
    request: RecoveryRequest,
    svc: RecoveryService = Depends(get_recovery_service),
) -> RecoveryPlan:
    """Generate a ranked list of recovery actions for a diagnosed fault."""
    return await svc.recommend(request)
