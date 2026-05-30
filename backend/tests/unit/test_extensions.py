from app.extensions import db, jwt, migrate


def test_singletons_exist():
    assert db is not None
    assert jwt is not None
    assert migrate is not None
