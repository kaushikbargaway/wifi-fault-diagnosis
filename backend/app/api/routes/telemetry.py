"""Telemetry ingestion endpoints."""

from fastapi import APIRouter, Depends
from app.schemas.telemetry import TelemetryCreate, TelemetryRead
from app.services.telemetry_service import TelemetryService
from app.api.dependencies import get_telemetry_service

router = APIRouter(prefix="/telemetry")


@router.post("/", response_model=TelemetryRead, status_code=201)
async def ingest_telemetry(
    payload: TelemetryCreate,
    svc: TelemetryService = Depends(get_telemetry_service),
) -> TelemetryRead:
    """Accept a telemetry reading from an ESP32 device or simulator."""
    return await svc.ingest(payload)


@router.get("/latest", response_model=TelemetryRead)
async def get_latest_telemetry(
    svc: TelemetryService = Depends(get_telemetry_service),
) -> TelemetryRead:
    """Return the most recent telemetry reading."""
    return await svc.get_latest()
