import pytest

from app import create_app
from app.config import TestConfig
from app.core.security.password import hash_password
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.extensions import db


@pytest.fixture()
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        db.session.add(
            HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas")
        )
        db.session.add(
            User(
                id=1,
                name="A",
                email="a@x.id",
                password_hash=hash_password("good", rounds=4),
                role="admin",
                facility_id=1,
            )
        )
        db.session.commit()
        yield app.test_client()


def test_login_success(client):
    resp = client.post("/api/auth/login", json={"email": "a@x.id", "password": "good"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["access_token"] and body["refresh_token"]
    assert body["user"]["role"] == "admin"


def test_login_bad_password(client):
    resp = client.post("/api/auth/login", json={"email": "a@x.id", "password": "bad"})
    assert resp.status_code == 401
    assert resp.get_json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"


def test_refresh_rotates(client):
    login = client.post("/api/auth/login", json={"email": "a@x.id", "password": "good"})
    refresh = login.get_json()["refresh_token"]
    resp = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    assert resp.get_json()["refresh_token"] != refresh


def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_failed_login_persists_audit(client):
    from sqlalchemy import select

    from app.db.models.audit_log import AuditLog
    from app.extensions import db

    client.post("/api/auth/login", json={"email": "a@x.id", "password": "wrong"})
    row = db.session.scalar(select(AuditLog).where(AuditLog.action == "login_failed"))
    assert row is not None


def test_refresh_replay_revokes_chain(client):
    # Log in, rotate once, then replay the original refresh token. The replay
    # must be rejected AND the successor token must be revoked (C1).
    login = client.post(
        "/api/auth/login", json={"email": "a@x.id", "password": "good"}
    ).get_json()
    original = login["refresh_token"]
    rotated = client.post("/api/auth/refresh", json={"refresh_token": original})
    assert rotated.status_code == 200
    successor = rotated.get_json()["refresh_token"]

    replay = client.post("/api/auth/refresh", json={"refresh_token": original})
    assert replay.status_code == 401
    assert replay.get_json()["error"]["code"] == "AUTH_REFRESH_REPLAY"

    # The successor token issued before the replay must now be dead.
    after = client.post("/api/auth/refresh", json={"refresh_token": successor})
    assert after.status_code == 401


def test_inactive_user_cannot_refresh(client):
    from app.db.models.user import User
    from app.extensions import db

    login = client.post(
        "/api/auth/login", json={"email": "a@x.id", "password": "good"}
    ).get_json()
    user = db.session.get(User, 1)
    user.is_active = False
    db.session.commit()

    resp = client.post("/api/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert resp.status_code == 401



def test_logout_then_me(client):
    login = client.post(
        "/api/auth/login", json={"email": "a@x.id", "password": "good"}
    ).get_json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}
    assert (
        client.post(
            "/api/auth/logout",
            json={"refresh_token": login["refresh_token"]},
            headers=headers,
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/auth/logout",
            json={"refresh_token": login["refresh_token"]},
            headers=headers,
        ).status_code
        == 200
    )
