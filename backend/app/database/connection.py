"""Database connection and session management (placeholder).

Will use SQLAlchemy async engine once the ORM models are finalised.
"""

from app.core.config import settings


def get_database_url() -> str:
    """Return the configured database URL."""
    return settings.DATABASE_URL


# TODO: Replace with async SQLAlchemy setup:
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
#
# engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
# AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#
# async def get_session() -> AsyncGenerator[AsyncSession, None]:
#     async with AsyncSessionLocal() as session:
#         yield session
