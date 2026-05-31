"""Encounter API integration tests."""
import pytest

from app.core.security.password import hash_password
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.extensions import db

_ROLES = {
    "admin": "admin@x.id",
    "clinician": "clinician@x.id",
    "nurse": "nurse@x.id",
    "researcher": "researcher@x.id",
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


def test_create_encounter(client):
    p = _register(client)
    resp = client.post(
        "/api/encounters",
        json={
            "patient_id": p["id"],
            "encounter_type": "rawat_jalan",
            "chief_complaint": "Nyeri dada 2 jam",
        },
        headers=_headers(client),
    )
    assert resp.status_code == 201
    assert resp.get_json()["encounter"]["status"] == "open"


def test_create_encounter_researcher_forbidden(client):
    p = _register(client)
    resp = client.post(
        "/api/encounters",
        json={"patient_id": p["id"]},
        headers=_headers(client, "researcher"),
    )
    assert resp.status_code == 403


def test_get_encounter(client):
    p = _register(client)
    created = client.post(
        "/api/encounters",
        json={"patient_id": p["id"]},
        headers=_headers(client),
    ).get_json()["encounter"]
    resp = client.get(
        f"/api/encounters/{created['id']}", headers=_headers(client)
    )
    assert resp.status_code == 200
    assert resp.get_json()["id"] == created["id"]


def test_close_encounter_idempotent(client):
    p = _register(client)
    created = client.post(
        "/api/encounters",
        json={"patient_id": p["id"]},
        headers=_headers(client),
    ).get_json()["encounter"]
    first = client.patch(
        f"/api/encounters/{created['id']}/close", headers=_headers(client)
    )
    assert first.status_code == 200
    second = client.patch(
        f"/api/encounters/{created['id']}/close", headers=_headers(client)
    )
    assert second.status_code == 200


def test_encounter_blocked_without_data_use_consent(client):
    """AC-8: encounter creation requires data_use consent."""
    p = _register(client)
    # Revoke data_use consent
    client.post(
        f"/api/patients/{p['id']}/consent",
        json={"consent_type": "data_use", "status": "revoked"},
        headers=_headers(client),
    )
    resp = client.post(
        "/api/encounters",
        json={"patient_id": p["id"]},
        headers=_headers(client),
    )
    assert resp.status_code == 403
    assert resp.get_json()["error"]["code"] == "CONSENT_REQUIRED"
