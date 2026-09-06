"""Simulate the effect of a recovery action in the Digital Twin (placeholder)."""

from app.schemas.digital_twin import SimulationRequest, SimulationResult
from app.digital_twin.twin_state import get_current_state


def simulate_action(request: SimulationRequest) -> SimulationResult:
    """Predict the network state after applying a recovery action.

    TODO: Apply the action in the VM environment, measure the outcome,
    and return the resulting state. Currently returns a placeholder.
    """
    predicted_state = get_current_state()
    return SimulationResult(
        action=request.action,
        predicted_state=predicted_state,
        improvement_score=0.0,
        notes="Simulation not yet connected to VM environment.",
    )
