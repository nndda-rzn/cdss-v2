"""Consent and PatientHistory API integration tests."""
import pytest

from app.core.security.password import hash_password
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.extensions import db

_ROLES = {
    "admin": "admin@x.id",
    "clinician": "clinician@x.id",
    "nurse": "nurse@x.id",
}


@pytest.fixture()
def client(app):
    with app.app_context():
        db.session.add(
            HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas")
        )
        for i, (role, email) in enumerate(_ROLES.items(), start=1):
            db.session.add(
                User(
                    id=i, name=role, email=email,
                    password_hash=hash_password("StrongPass1", rounds=4),
                    role=role, facility_id=1,
                )
            )
        db.session.commit()
        yield app.test_client()


def _headers(client, role="clinician"):
    resp = client.post(
        "/api/auth/login", json={"email": _ROLES[role], "password": "StrongPass1"}
    )
    return {"Authorization": f"Bearer {resp.get_json()['access_token']}"}


def _register(client):
    resp = client.post(
        "/api/patients",
        json={
            "name": "Budi Santoso",
            "dob": "1965-03-12",
            "gender": "male",
            "consent_data_use": True,
        },
        headers=_headers(client),
    )
    return resp.get_json()["patient"]


def test_capture_consent(client):
    p = _register(client)
    resp = client.post(
        f"/api/patients/{p['id']}/consent",
        json={"consent_type": "ai_analysis"},
        headers=_headers(client),
    )
    assert resp.status_code == 201


def test_list_consent(client):
    p = _register(client)
    # data_use captured at register
    resp = client.get(
        f"/api/patients/{p['id']}/consent", headers=_headers(client)
    )
    assert resp.status_code == 200
    types = {c["consent_type"] for c in resp.get_json()["items"]}
    assert "data_use" in types


def test_revoke_consent(client):
    p = _register(client)
    resp = client.post(
        f"/api/patients/{p['id']}/consent",
        json={"consent_type": "data_use", "status": "revoked"},
        headers=_headers(client),
    )
    assert resp.status_code == 201


def test_add_and_list_history(client):
    p = _register(client)
    add = client.post(
        f"/api/patients/{p['id']}/history",
        json={"condition_code": "MI", "note": "infark 2020"},
        headers=_headers(client),
    )
    assert add.status_code == 201
    listing = client.get(
        f"/api/patients/{p['id']}/history", headers=_headers(client)
    )
    assert listing.status_code == 200
    assert listing.get_json()["items"][0]["condition_code"] == "MI"
