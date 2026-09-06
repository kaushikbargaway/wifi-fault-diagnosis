"""Pydantic schemas for telemetry data transfer."""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class TelemetryCreate(BaseModel):
    """Schema for incoming telemetry from ESP32 or simulator."""

    device_id: str = Field(..., description="Unique identifier of the reporting device")
    timestamp: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO-8601 timestamp; server time used if omitted",
    )

    # Network metrics - all optional because different sources may omit some
    rssi_dbm: Optional[float] = Field(None, ge=-120.0, le=0.0, description="RSSI in dBm")
    latency_ms: Optional[float] = Field(None, ge=0.0, description="Round-trip latency in ms")
    packet_loss_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Packet loss %")
    internet_reachable: Optional[bool] = Field(None, description="True if WAN reachable")
    dns_available: Optional[bool] = Field(None, description="True if DNS resolution succeeded")
    ethernet_connected: Optional[bool] = Field(None, description="True if Ethernet link is up")
    temperature_c: Optional[float] = Field(None, description="Device/router temperature in C")
    network_load: Optional[float] = Field(None, ge=0.0, le=100.0, description="Network utilisation %")


class TelemetryRead(TelemetryCreate):
    """Schema returned when reading stored telemetry."""

    id: int
    fault_label: Optional[str] = None  # populated after diagnosis

    model_config = {"from_attributes": True}
