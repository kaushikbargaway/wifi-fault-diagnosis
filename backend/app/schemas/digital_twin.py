"""Pydantic schemas for the Digital Twin layer."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NetworkNode(BaseModel):
    """Represents a single node in the simulated network topology."""

    node_id: str
    node_type: str  # e.g. "router", "switch", "access_point", "client"
    status: str = "unknown"  # up | down | degraded | unknown
    metrics: Dict[str, Any] = Field(default_factory=dict)


class TwinState(BaseModel):
    """Current state of the Digital Twin."""

    nodes: List[NetworkNode] = Field(default_factory=list)
    overall_health: str = "unknown"  # healthy | degraded | faulty | unknown
    last_synced: Optional[str] = None  # ISO-8601 timestamp
    fault_label: Optional[str] = None  # mirrored from diagnosis


class SimulationRequest(BaseModel):
    """Request to simulate a recovery action in the Digital Twin."""

    action: str = Field(..., description="Recovery action to simulate")
    target_node: Optional[str] = Field(None, description="Node the action targets")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SimulationResult(BaseModel):
    """Result of a Digital Twin simulation."""

    action: str
    predicted_state: TwinState
    improvement_score: float = Field(..., ge=0.0, le=1.0)
    notes: str = ""
