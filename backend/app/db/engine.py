"""Engine factory with pragmas wired in."""
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.db.pragmas import register_sqlite_pragmas


def create_db_engine(url: str) -> Engine:
    engine = create_engine(url, future=True)
    if url.startswith("sqlite"):
        register_sqlite_pragmas(engine)
    return engine
