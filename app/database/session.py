from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
_database_initialized = False


def init_database() -> None:
    global _database_initialized
    if _database_initialized:
        return

    from app.database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _database_initialized = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
