"""ORM model for Digital Twin state snapshots (placeholder)."""

from datetime import datetime
from typing import Dict, Any


class TwinSnapshot:
    """A point-in-time snapshot of the Digital Twin state."""

    id: int
    timestamp: datetime
    state: Dict[str, Any]  # serialised twin state
