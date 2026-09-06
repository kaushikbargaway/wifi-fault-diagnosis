"""Digital Twin service — manages twin state and simulation."""

import logging
from app.schemas.digital_twin import TwinState, SimulationRequest, SimulationResult
from app.digital_twin.twin_state import get_current_state
from app.digital_twin.recovery_simulator import simulate_action

logger = logging.getLogger(__name__)


class DigitalTwinService:
    """Thin orchestration layer between the API and the Digital Twin module."""

    async def get_state(self) -> TwinState:
        """Retrieve and return the current Digital Twin state."""
        state = get_current_state()
        logger.info("Digital Twin state retrieved: health=%s", state.overall_health)
        return state

    async def simulate(self, request: SimulationRequest) -> SimulationResult:
        """Simulate a recovery action and return the predicted outcome."""
        result = simulate_action(request)
        logger.info("Simulation complete: action=%s improvement=%.2f", request.action, result.improvement_score)
        return result
