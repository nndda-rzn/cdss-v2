"""Dashboard API integration tests."""
import pytest

from app.core.security.password import hash_password
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.extensions import db

_ROLES = {"admin": "admin@x.id", "clinician": "clinician@x.id"}


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


def _headers(client, role="admin"):
    resp = client.post(
        "/api/auth/login", json={"email": _ROLES[role], "password": "StrongPass1"}
    )
    return {"Authorization": f"Bearer {resp.get_json()['access_token']}"}


def test_dashboard_stats_returns_zeros_on_empty(client):
    resp = client.get("/api/dashboard/stats", headers=_headers(client))
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total_patients"] == 0
    assert body["active_encounters"] == 0
    assert body["analyses_today"] == 0
    assert body["pending_tasks"] == 0
    assert body["recent_encounters"] == []


def test_dashboard_stats_after_patient_and_encounter(client):
    h = _headers(client, role="clinician")
    p = client.post(
        "/api/patients",
        json={
            "name": "Budi Santoso", "dob": "1965-03-12", "gender": "male",
            "consent_data_use": True,
        },
        headers=h,
    ).get_json()["patient"]
    client.post("/api/encounters", json={"patient_id": p["id"]}, headers=h)

    resp = client.get("/api/dashboard/stats", headers=_headers(client))
    body = resp.get_json()
    assert body["total_patients"] == 1
    assert body["active_encounters"] == 1
    assert body["pending_tasks"] == 1
    assert len(body["recent_encounters"]) == 1
    row = body["recent_encounters"][0]
    assert row["status"] == "open"
    assert row["encounter_type"] == "rawat_jalan"
    assert "started_at" in row


def test_dashboard_requires_auth(client):
    resp = client.get("/api/dashboard/stats")
    assert resp.status_code == 401


def test_dashboard_scoped_by_facility(client):
    """A user from facility 2 must not see facility 1 counts."""
    with client.application.app_context():
        db.session.add(
            HealthcareFacility(id=2, name="Q", code="Q1", facility_type="puskesmas")
        )
        db.session.add(
            User(
                id=99, name="other", email="other@y.id",
                password_hash=hash_password("StrongPass1", rounds=4),
                role="admin", facility_id=2,
            )
        )
        db.session.commit()

    # Seed a patient in facility 1.
    h1 = _headers(client, role="clinician")
    client.post(
        "/api/patients",
        json={
            "name": "Xavier Yansen", "dob": "1980-01-01", "gender": "male",
            "consent_data_use": True,
        },
        headers=h1,
    )

    # Login as facility-2 user.
    other = client.post(
        "/api/auth/login", json={"email": "other@y.id", "password": "StrongPass1"}
    ).get_json()
    h2 = {"Authorization": f"Bearer {other['access_token']}"}

    resp = client.get("/api/dashboard/stats", headers=h2)
    body = resp.get_json()
    assert body["total_patients"] == 0
    assert body["active_encounters"] == 0
