"""Telemetry service - receives, validates, and stores telemetry readings."""

import logging
from app.schemas.telemetry import TelemetryCreate, TelemetryRead

logger = logging.getLogger(__name__)


class TelemetryService:
    """Handles all telemetry ingestion and retrieval logic.

    In the current placeholder implementation data is held in memory.
    Replace _store with a proper database repository in phase 2.
    """

    def __init__(self) -> None:
        self._store: list[TelemetryRead] = []
        self._counter: int = 0

    async def ingest(self, payload: TelemetryCreate) -> TelemetryRead:
        """Store an incoming telemetry reading."""
        self._counter += 1
        record = TelemetryRead(id=self._counter, **payload.model_dump())
        self._store.append(record)
        logger.info("Ingested telemetry id=%d from device=%s", self._counter, payload.device_id)
        return record

    async def get_latest(self) -> TelemetryRead:
        """Return the most recently ingested reading."""
        if not self._store:
            raise ValueError("No telemetry data available yet.")
        return self._store[-1]
