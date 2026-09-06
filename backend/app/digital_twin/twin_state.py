"""Digital Twin state management (placeholder).

This module maintains the current network state mirrored from:
- Real telemetry (synced from the backend)
- Ubuntu VM network metrics (collected via SSH or an agent)
"""

from app.schemas.digital_twin import TwinState, NetworkNode


def get_current_state() -> TwinState:
    """Return the current Digital Twin state.

    TODO: Replace with real state that is synchronised from:
    - Telemetry readings
    - VM1 / VM2 metrics collected over SSH
    """
    # Placeholder — returns a minimal static topology
    return TwinState(
        nodes=[
            NetworkNode(node_id="router",  node_type="router",     status="unknown"),
            NetworkNode(node_id="vm1",     node_type="server",     status="unknown"),
            NetworkNode(node_id="vm2",     node_type="server",     status="unknown"),
            NetworkNode(node_id="esp32",   node_type="iot_sensor", status="unknown"),
        ],
        overall_health="unknown",
        last_synced=None,
        fault_label=None,
    )


def update_state_from_telemetry(state: TwinState, telemetry: dict) -> TwinState:
    """Update the twin state with the latest telemetry values (placeholder)."""
    # TODO: Map telemetry fields to the appropriate node metrics.
    return state
