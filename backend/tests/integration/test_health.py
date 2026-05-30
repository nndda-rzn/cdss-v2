from app import create_app
from app.config import TestConfig


def test_health_ok():
    app = create_app(TestConfig)
    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert body["db"] == "ok"


def test_version():
    app = create_app(TestConfig)
    client = app.test_client()
    resp = client.get("/api/version")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "version" in body and "git_sha" in body
