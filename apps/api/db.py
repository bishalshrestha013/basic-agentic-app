"""SQLAlchemy engine, session factory, and database initialisation."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import get_settings

_settings = get_settings()

engine = create_engine(
    _settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create the SQLite file and tables if they do not exist."""
    from models import Base

    Base.metadata.create_all(bind=engine)


def get_session() -> Iterator[Session]:
    """Yield a session and guarantee it is closed."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
