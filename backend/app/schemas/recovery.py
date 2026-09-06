"""Pydantic schemas for recovery recommendations."""

from typing import List
from pydantic import BaseModel, Field
from app.schemas.diagnosis import DiagnosisResult


class RecoveryAction(BaseModel):
    """A single recommended recovery action."""

    action: str = Field(..., description="Short action description")
    reason: str = Field(..., description="Why this action is recommended")
    expected_result: str = Field(..., description="What improvement is expected")
    priority: int = Field(..., ge=1, description="1 = highest priority")


class RecoveryRequest(BaseModel):
    """Input for the recovery recommendation engine."""

    diagnosis: DiagnosisResult


class RecoveryPlan(BaseModel):
    """Ordered list of recovery actions for a diagnosed fault."""

    fault_label: str
    actions: List[RecoveryAction]
