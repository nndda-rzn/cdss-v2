"""Shared pytest fixtures.

Guards against touching the real data/cdss.db: TestConfig uses in-memory,
and any file-based fixtures use tmp_path only.
"""
import os
from typing import cast

import pytest
from cryptography.fernet import Fernet
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from app import create_app
from app.config import TestConfig
from app.core.encryption.fernet_provider import FernetProvider
from app.core.encryption.hash_provider import HashProvider
from app.core.security.password import hash_password
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.db.types.context import set_crypto
from app.extensions import db as _db


@pytest.fixture(autouse=True)
def _guard_real_db() -> None:
    """Fail fast if a test is ever pointed at the real database file."""
    url = os.environ.get("DATABASE_URL", "")
    assert "cdss.db" not in url or ":memory:" in TestConfig().SQLALCHEMY_DATABASE_URI, (
        "Tests must not target the real database"
    )


@pytest.fixture()
def app() -> object:
    set_crypto(FernetProvider(Fernet.generate_key()), HashProvider(b"test-pepper"))
    application: Flask = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def session(app: Flask) -> Session:
    return cast(Session, _db.session)


@pytest.fixture()
def seeded_admin(session: Session) -> dict[str, str]:
    session.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
    session.add(
        User(
            id=1,
            name="Admin",
            email="admin@x.id",
            password_hash=hash_password("StrongPass1", rounds=4),
            role="admin",
            facility_id=1,
        )
    )
    session.commit()
    return {"email": "admin@x.id", "password": "StrongPass1"}


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()
