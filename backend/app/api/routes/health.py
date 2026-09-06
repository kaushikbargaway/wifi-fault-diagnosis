"""Health / status endpoint."""

from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Return basic health information about the running service."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "wifi-fault-diagnosis-backend",
    }
