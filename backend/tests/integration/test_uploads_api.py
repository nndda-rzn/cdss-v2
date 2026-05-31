"""Uploads API integration tests (RBAC + path traversal + content type)."""

import pytest

from app.core.security.password import hash_password
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.extensions import db

_ROLES = {"clinician": "clinician@x.id", "researcher": "researcher@x.id"}

_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


@pytest.fixture()
def client(app, tmp_path):
    app.config["STORAGE_DIR"] = str(tmp_path)
    # Seed a real file under uploads/ecg/.
    target = tmp_path / "uploads" / "ecg" / "1" / "1" / "ECG-P1-x.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(_PNG)
    with app.app_context():
        db.session.add(
            HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas")
        )
        for i, (role, email) in enumerate(_ROLES.items(), start=1):
            db.session.add(
                User(id=i, name=role, email=email,
                     password_hash=hash_password("StrongPass1", rounds=4),
                     role=role, facility_id=1)
            )
        db.session.commit()
        yield app.test_client()


def _headers(client, role="clinician"):
    resp = client.post(
        "/api/auth/login", json={"email": _ROLES[role], "password": "StrongPass1"}
    )
    return {"Authorization": f"Bearer {resp.get_json()['access_token']}"}


def test_serve_existing_image(client):
    resp = client.get("/uploads/ecg/1/1/ECG-P1-x.png", headers=_headers(client))
    assert resp.status_code == 200
    assert resp.mimetype == "image/png"
    assert resp.data == _PNG


def test_serve_requires_auth(client):
    resp = client.get("/uploads/ecg/1/1/ECG-P1-x.png")
    assert resp.status_code == 401


def test_serve_missing_file_404(client):
    resp = client.get("/uploads/ecg/9/9/nope.png", headers=_headers(client))
    assert resp.status_code == 404
    assert resp.get_json()["error"]["code"] == "FILE_NOT_FOUND"


def test_reject_path_traversal(client):
    resp = client.get("/uploads/ecg/../../secrets/master.key", headers=_headers(client))
    # Either our guard (422) or werkzeug normalisation (404) — never 200.
    assert resp.status_code in (404, 422)
    assert resp.status_code != 200


def test_reject_outside_whitelist(client):
    resp = client.get("/uploads/other/file.png", headers=_headers(client))
    assert resp.status_code == 422
    assert resp.get_json()["error"]["code"] == "INVALID_PATH"


def test_researcher_can_read(client):
    resp = client.get(
        "/uploads/ecg/1/1/ECG-P1-x.png", headers=_headers(client, role="researcher")
    )
    assert resp.status_code == 200
