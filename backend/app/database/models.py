"""
SQLAlchemy ORM models — database table definitions.

Tables:
  telemetry_records  — one row per telemetry reading
  diagnosis_records  — one row per ML diagnosis result
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, Float, Boolean, String,
    DateTime, JSON, ForeignKey, Index,
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


class TelemetryRecord(Base):
    """Stores one network telemetry reading from any source."""

    __tablename__ = "telemetry_records"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    device_id            = Column(String(64), nullable=False, index=True)
    timestamp            = Column(DateTime(timezone=True), nullable=False,
                                  default=lambda: datetime.now(timezone.utc))
    created_at           = Column(DateTime(timezone=True), nullable=False,
                                  default=lambda: datetime.now(timezone.utc))

    # Network quality metrics (nullable — source may not report all fields)
    rssi_dbm             = Column(Float,   nullable=True)
    latency_ms           = Column(Float,   nullable=True)
    packet_loss_percent  = Column(Float,   nullable=True)
    jitter_ms            = Column(Float,   nullable=True)

    # Connectivity flags
    internet_reachable   = Column(Boolean, nullable=True)
    dns_available        = Column(Boolean, nullable=True)
    ethernet_connected   = Column(Boolean, nullable=True)

    # System metrics
    temperature_c        = Column(Float,   nullable=True)
    network_load         = Column(Float,   nullable=True)
    cpu_usage_percent    = Column(Float,   nullable=True)
    memory_usage_percent = Column(Float,   nullable=True)

    # Fault label — set after diagnosis
    fault_label          = Column(String(64), nullable=True)

    # Back-reference to diagnoses
    diagnoses = relationship("DiagnosisRecord", back_populates="telemetry", cascade="all, delete-orphan")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_telemetry_device_ts", "device_id", "timestamp"),
    )

    def to_dict(self) -> dict:
        return {
            "id":                   self.id,
            "device_id":            self.device_id,
            "timestamp":            self.timestamp.isoformat() if self.timestamp else None,
            "rssi_dbm":             self.rssi_dbm,
            "latency_ms":           self.latency_ms,
            "packet_loss_percent":  self.packet_loss_percent,
            "internet_reachable":   self.internet_reachable,
            "dns_available":        self.dns_available,
            "ethernet_connected":   self.ethernet_connected,
            "temperature_c":        self.temperature_c,
            "network_load":         self.network_load,
            "fault_label":          self.fault_label,
        }


class DiagnosisRecord(Base):
    """Stores one ML diagnosis result linked to a telemetry reading."""

    __tablename__ = "diagnosis_records"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    timestamp      = Column(DateTime(timezone=True), nullable=False,
                            default=lambda: datetime.now(timezone.utc))
    created_at     = Column(DateTime(timezone=True), nullable=False,
                            default=lambda: datetime.now(timezone.utc))

    fault_label    = Column(String(64),  nullable=False, index=True)
    confidence     = Column(Float,       nullable=False)
    probabilities  = Column(JSON,        nullable=False, default=dict)

    # Link back to the telemetry that triggered this diagnosis
    telemetry_id   = Column(Integer, ForeignKey("telemetry_records.id",
                            ondelete="SET NULL"), nullable=True)
    telemetry      = relationship("TelemetryRecord", back_populates="diagnoses")

    __table_args__ = (
        Index("ix_diagnosis_fault_ts", "fault_label", "timestamp"),
    )

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "timestamp":     self.timestamp.isoformat() if self.timestamp else None,
            "fault_label":   self.fault_label,
            "confidence":    self.confidence,
            "probabilities": self.probabilities,
            "telemetry_id":  self.telemetry_id,
        }
