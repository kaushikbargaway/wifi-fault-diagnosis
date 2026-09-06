"""Pydantic schemas for fault diagnosis."""

from datetime import datetime, timezone
from typing import Dict, Optional
from pydantic import BaseModel, Field
from app.schemas.telemetry import TelemetryCreate


class DiagnosisRequest(BaseModel):
    """Input for a diagnosis request - wraps a telemetry reading."""

    telemetry: TelemetryCreate


class DiagnosisResult(BaseModel):
    """Output of the fault diagnosis model."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    fault_label: str = Field(..., description="Predicted fault class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence 0-1")
    probabilities: Dict[str, float] = Field(
        ..., description="Per-class probability scores"
    )
    telemetry: Optional[TelemetryCreate] = None
