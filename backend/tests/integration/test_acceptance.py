"""Sprint 1 acceptance criteria AC-1..AC-13 (automatable subset)."""
from sqlalchemy import select

from app.db.models.audit_log import AuditLog


def test_ac5_login_returns_tokens(client, seeded_admin):
    resp = client.post("/api/auth/login", json=seeded_admin)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["access_token"] and body["refresh_token"]


def test_ac6_refresh_rotation(client, seeded_admin):
    login = client.post("/api/auth/login", json=seeded_admin).get_json()
    resp = client.post("/api/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert resp.status_code == 200
    assert resp.get_json()["refresh_token"] != login["refresh_token"]


def test_ac7_rbac_blocks_without_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_ac8_audit_log_on_login(client, seeded_admin, session):
    client.post("/api/auth/login", json=seeded_admin)
    row = session.scalar(select(AuditLog).where(AuditLog.action == "login"))
    assert row is not None


def test_ac9_health_and_version(client):
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/version").status_code == 200


def test_ac9_health_db_probe(client):
    body = client.get("/api/health").get_json()
    assert body["db"] == "ok"
