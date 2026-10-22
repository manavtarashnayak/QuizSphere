"""SQLAlchemy engine and database-session dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class for future SQLAlchemy models."""


def get_db() -> Generator[Session, None, None]:
    """Yield one database session and always close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> None:
    """Raise an exception when PostgreSQL cannot service a basic query."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
