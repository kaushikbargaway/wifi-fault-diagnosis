"""
SQLAlchemy database connection and session management.

Uses synchronous SQLAlchemy with SQLite for simplicity.
SQLite is appropriate for development and single-node deployment.
Switch DATABASE_URL in .env to PostgreSQL for production.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Engine
# ─────────────────────────────────────────────────────────────────────────────

# connect_args is SQLite-specific — allows same connection across threads
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,   # log SQL in debug mode
)

# Enable WAL mode on SQLite for better concurrent read performance
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ─────────────────────────────────────────────────────────────────────────────
# Session factory
# ─────────────────────────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db():
    """Dependency-injected database session — use in FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Base class for ORM models
# ─────────────────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Table creation
# ─────────────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create all tables if they do not already exist.
    Called once on application startup.
    """
    # Import models so SQLAlchemy registers them with Base.metadata
    from app.database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialised → %s", settings.DATABASE_URL)
