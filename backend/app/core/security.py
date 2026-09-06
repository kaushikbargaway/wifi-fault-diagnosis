"""Security utilities (placeholder).

Will hold API-key verification, JWT helpers, or other auth mechanisms
once the authentication strategy is finalised.
"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """Placeholder — currently unenforced. Enable in production."""
    # TODO: validate api_key against a stored secret when auth is needed.
    pass
