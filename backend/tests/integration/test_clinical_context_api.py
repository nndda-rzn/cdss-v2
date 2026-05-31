"""ClinicalContext API integration tests."""
import pytest

from app.core.security.password import hash_password
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.extensions import db

_ROLES = {"clinician": "clinician@x.id", "nurse": "nurse@x.id"}


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


def _encounter(client):
    p = client.post(
        "/api/patients",
        json={"name": "Budi Santoso", "dob": "1965-03-12", "gender": "male",
              "consent_data_use": True},
        headers=_headers(client),
    ).get_json()["patient"]
    return client.post(
        "/api/encounters", json={"patient_id": p["id"]}, headers=_headers(client)
    ).get_json()["encounter"]


def test_create_clinical_context(client):
    e = _encounter(client)
    resp = client.post(
        f"/api/encounters/{e['id']}/clinical-context",
        json={"symptom_chest_pain": True, "pain_onset_minutes": 120},
        headers=_headers(client),
    )
    assert resp.status_code == 201


def test_get_clinical_context(client):
    e = _encounter(client)
    client.post(
        f"/api/encounters/{e['id']}/clinical-context",
        json={"symptom_chest_pain": True},
        headers=_headers(client),
    )
    resp = client.get(
        f"/api/encounters/{e['id']}/clinical-context", headers=_headers(client)
    )
    assert resp.status_code == 200
    assert resp.get_json()["symptom_chest_pain"] is True


def test_duplicate_context_409(client):
    e = _encounter(client)
    client.post(
        f"/api/encounters/{e['id']}/clinical-context",
        json={"symptom_chest_pain": True},
        headers=_headers(client),
    )
    resp = client.post(
        f"/api/encounters/{e['id']}/clinical-context",
        json={"symptom_dyspnea": True},
        headers=_headers(client),
    )
    assert resp.status_code == 409
    assert resp.get_json()["error"]["code"] == "CLINICAL_CONTEXT_EXISTS"
