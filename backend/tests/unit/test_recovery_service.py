"""Unit tests for the RecoveryService."""

import pytest
from app.services.recovery_service import RecoveryService
from app.schemas.recovery import RecoveryRequest
from app.schemas.diagnosis import DiagnosisResult


@pytest.mark.asyncio
async def test_recommend_dns_failure():
    svc = RecoveryService()
    diagnosis = DiagnosisResult(
        fault_label="dns_failure",
        confidence=0.92,
        probabilities={"dns_failure": 0.92, "normal": 0.08},
    )
    plan = await svc.recommend(RecoveryRequest(diagnosis=diagnosis))
    assert plan.fault_label == "dns_failure"
    assert len(plan.actions) >= 1
    assert plan.actions[0].priority == 1
