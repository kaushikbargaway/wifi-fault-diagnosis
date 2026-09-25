"""
Repository classes — all database CRUD operations live here.
Services call repositories; repositories call SQLAlchemy.
This keeps SQL logic out of business logic.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import TelemetryRecord, DiagnosisRecord

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Telemetry Repository
# ─────────────────────────────────────────────────────────────────────────────

class TelemetryRepository:
    """CRUD operations for TelemetryRecord."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, data: dict) -> TelemetryRecord:
        """Insert a new telemetry record and return it with its generated id."""
        # Remove keys that aren't columns
        allowed = {c.name for c in TelemetryRecord.__table__.columns}
        clean   = {k: v for k, v in data.items() if k in allowed}

        record = TelemetryRecord(**clean)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        logger.debug("TelemetryRecord saved id=%d", record.id)
        return record

    def get_latest(self) -> Optional[TelemetryRecord]:
        """Return the most recently created telemetry record, or None."""
        return (
            self.db.query(TelemetryRecord)
            .order_by(TelemetryRecord.created_at.desc())
            .first()
        )

    def get_all(self, limit: int = 100) -> list[TelemetryRecord]:
        """Return up to `limit` records, newest first."""
        return (
            self.db.query(TelemetryRecord)
            .order_by(TelemetryRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_device(self, device_id: str, limit: int = 50) -> list[TelemetryRecord]:
        """Return records for a specific device, newest first."""
        return (
            self.db.query(TelemetryRecord)
            .filter(TelemetryRecord.device_id == device_id)
            .order_by(TelemetryRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    def update_fault_label(self, record_id: int, fault_label: str) -> None:
        """Set the fault_label on an existing telemetry record after diagnosis."""
        self.db.query(TelemetryRecord).filter(
            TelemetryRecord.id == record_id
        ).update({"fault_label": fault_label})
        self.db.commit()

    def count(self) -> int:
        """Total number of stored telemetry records."""
        return self.db.query(TelemetryRecord).count()


# ─────────────────────────────────────────────────────────────────────────────
# Diagnosis Repository
# ─────────────────────────────────────────────────────────────────────────────

class DiagnosisRepository:
    """CRUD operations for DiagnosisRecord."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, data: dict) -> DiagnosisRecord:
        """Insert a new diagnosis record and return it."""
        allowed = {c.name for c in DiagnosisRecord.__table__.columns}
        clean   = {k: v for k, v in data.items() if k in allowed}

        record = DiagnosisRecord(**clean)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        logger.debug("DiagnosisRecord saved id=%d fault=%s", record.id, record.fault_label)
        return record

    def get_history(self, limit: int = 20) -> list[DiagnosisRecord]:
        """Return the most recent `limit` diagnosis records."""
        return (
            self.db.query(DiagnosisRecord)
            .order_by(DiagnosisRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_fault(self, fault_label: str, limit: int = 50) -> list[DiagnosisRecord]:
        """Return diagnosis records matching a specific fault label."""
        return (
            self.db.query(DiagnosisRecord)
            .filter(DiagnosisRecord.fault_label == fault_label)
            .order_by(DiagnosisRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    def fault_counts(self) -> dict[str, int]:
        """Return a count of each fault label seen so far."""
        from sqlalchemy import func
        rows = (
            self.db.query(DiagnosisRecord.fault_label, func.count().label("n"))
            .group_by(DiagnosisRecord.fault_label)
            .all()
        )
        return {row.fault_label: row.n for row in rows}

    def count(self) -> int:
        """Total number of stored diagnosis records."""
        return self.db.query(DiagnosisRecord).count()
