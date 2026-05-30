from app.db.engine import create_db_engine
from app.db.session import make_session_factory


def test_session_factory_yields_working_session(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 't.db'}")
    Session = make_session_factory(engine)  # noqa: N806
    from sqlalchemy import text
    with Session() as s:
        assert s.execute(text("SELECT 1")).scalar() == 1
