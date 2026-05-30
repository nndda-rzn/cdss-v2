from app.db.engine import create_db_engine


def test_engine_applies_pragmas(tmp_path):
    db = tmp_path / "t.db"
    engine = create_db_engine(f"sqlite:///{db}")
    from sqlalchemy import text
    with engine.connect() as conn:
        assert conn.execute(text("PRAGMA foreign_keys")).scalar() == 1
