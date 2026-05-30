from app.db.base import Base


def test_base_has_metadata():
    assert hasattr(Base, "metadata")
    assert Base.metadata.tables == {} or isinstance(Base.metadata.tables, dict)
