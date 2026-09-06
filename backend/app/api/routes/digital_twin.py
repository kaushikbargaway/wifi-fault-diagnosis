"""Digital Twin state and simulation endpoints."""

from fastapi import APIRouter, Depends
from app.schemas.digital_twin import TwinState, SimulationRequest, SimulationResult
from app.services.digital_twin_service import DigitalTwinService
from app.api.dependencies import get_digital_twin_service

router = APIRouter(prefix="/digital-twin")


@router.get("/state", response_model=TwinState)
async def get_state(
    svc: DigitalTwinService = Depends(get_digital_twin_service),
) -> TwinState:
    """Return the current Digital Twin state."""
    return await svc.get_state()


@router.post("/simulate", response_model=SimulationResult)
async def simulate_recovery(
    request: SimulationRequest,
    svc: DigitalTwinService = Depends(get_digital_twin_service),
) -> SimulationResult:
    """Simulate a recovery action and return the predicted outcome."""
    return await svc.simulate(request)
