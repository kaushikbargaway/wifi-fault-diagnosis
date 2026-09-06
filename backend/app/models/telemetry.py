"""ORM model for telemetry readings (placeholder).

Will map to the `telemetry` table once the database layer is wired up.
"""

from datetime import datetime
from typing import Optional

# TODO: Replace with a real SQLAlchemy/SQLModel Base once the DB is configured.


class TelemetryRecord:
    """Represents a single telemetry snapshot from a device."""

    id: int
    timestamp: datetime
    device_id: str
    rssi_dbm: Optional[float]
    latency_ms: Optional[float]
    packet_loss_percent: Optional[float]
    internet_reachable: Optional[bool]
    dns_available: Optional[bool]
    ethernet_connected: Optional[bool]
    temperature_c: Optional[float]
    network_load: Optional[float]
    fault_label: Optional[str]  # populated after diagnosis
