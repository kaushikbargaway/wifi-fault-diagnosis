"""Repository pattern for database access (placeholder).

Each repository encapsulates all database operations for one entity type,
keeping SQL/ORM logic out of service classes.
"""


class TelemetryRepository:
    """CRUD operations for TelemetryRecord (placeholder)."""

    async def save(self, record: dict) -> dict:
        raise NotImplementedError

    async def get_latest(self) -> dict:
        raise NotImplementedError

    async def get_all(self, limit: int = 100) -> list:
        raise NotImplementedError


class DiagnosisRepository:
    """CRUD operations for DiagnosisRecord (placeholder)."""

    async def save(self, record: dict) -> dict:
        raise NotImplementedError

    async def get_history(self, limit: int = 20) -> list:
        raise NotImplementedError
