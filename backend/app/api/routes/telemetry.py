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
    """Accept a telemetry reading from ESP32, simulator, or collector script."""
    return await svc.ingest(payload)


@router.get("/latest", response_model=TelemetryRead)
async def get_latest_telemetry(
    svc: TelemetryService = Depends(get_telemetry_service),
) -> TelemetryRead:
    """Return the most recent telemetry reading from the database."""
    return await svc.get_latest()


@router.get("/history", response_model=list[TelemetryRead])
async def get_telemetry_history(
    limit: int = 50,
    svc: TelemetryService = Depends(get_telemetry_service),
) -> list[TelemetryRead]:
    """Return the most recent telemetry readings (default: last 50)."""
    return await svc.get_all(limit=limit)


@router.get("/count")
async def get_telemetry_count(
    svc: TelemetryService = Depends(get_telemetry_service),
) -> dict:
    """Return total number of stored telemetry records."""
    return {"count": await svc.get_count()}
