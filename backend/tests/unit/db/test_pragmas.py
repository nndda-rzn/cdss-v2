from sqlalchemy import create_engine, text

from app.db.pragmas import register_sqlite_pragmas


def test_foreign_keys_enabled(tmp_path):
    db = tmp_path / "t.db"
    engine = create_engine(f"sqlite:///{db}")
    register_sqlite_pragmas(engine)
    with engine.connect() as conn:
        assert conn.execute(text("PRAGMA foreign_keys")).scalar() == 1
        assert conn.execute(text("PRAGMA journal_mode")).scalar().lower() == "wal"
