"""Telemetry service — receives, validates, and persists telemetry readings."""

import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.telemetry import TelemetryCreate, TelemetryRead
from app.database.repositories import TelemetryRepository

logger = logging.getLogger(__name__)


class TelemetryService:
    """Handles all telemetry ingestion and retrieval using SQLite persistence."""

    def __init__(self, db: Session) -> None:
        self.repo = TelemetryRepository(db)

    async def ingest(self, payload: TelemetryCreate) -> TelemetryRead:
        """Persist an incoming telemetry reading and return it with its DB id."""
        data = payload.model_dump()

        # Convert datetime to string for storage compatibility
        if data.get("timestamp") and hasattr(data["timestamp"], "isoformat"):
            data["timestamp"] = data["timestamp"]

        record = self.repo.save(data)
        logger.info(
            "Telemetry ingested id=%d device=%s latency=%.1fms loss=%.1f%%",
            record.id,
            record.device_id,
            record.latency_ms or 0,
            record.packet_loss_percent or 0,
        )

        return TelemetryRead(
            id=record.id,
            **payload.model_dump(),
        )

    async def get_latest(self) -> TelemetryRead:
        """Return the most recently ingested reading from the database."""
        record = self.repo.get_latest()
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No telemetry data available yet. "
                       "Send a POST /api/v1/telemetry/ request first.",
            )
        return TelemetryRead(**record.to_dict())

    async def get_all(self, limit: int = 100) -> list[TelemetryRead]:
        """Return the most recent telemetry records."""
        records = self.repo.get_all(limit=limit)
        return [TelemetryRead(**r.to_dict()) for r in records]

    async def get_count(self) -> int:
        """Return total number of stored readings."""
        return self.repo.count()
