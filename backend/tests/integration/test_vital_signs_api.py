"""VitalSigns API integration tests."""
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


def test_capture_vitals(client):
    e = _encounter(client)
    resp = client.post(
        f"/api/encounters/{e['id']}/vital-signs",
        json={"bp_systolic": 140, "bp_diastolic": 90, "heart_rate": 110},
        headers=_headers(client),
    )
    assert resp.status_code == 201


def test_capture_vitals_empty_422(client):
    e = _encounter(client)
    resp = client.post(
        f"/api/encounters/{e['id']}/vital-signs",
        json={},
        headers=_headers(client),
    )
    assert resp.status_code == 422
    assert resp.get_json()["error"]["code"] == "VITALS_EMPTY"


def test_list_vitals_desc(client):
    e = _encounter(client)
    client.post(
        f"/api/encounters/{e['id']}/vital-signs",
        json={"heart_rate": 100},
        headers=_headers(client),
    )
    client.post(
        f"/api/encounters/{e['id']}/vital-signs",
        json={"heart_rate": 95},
        headers=_headers(client),
    )
    resp = client.get(
        f"/api/encounters/{e['id']}/vital-signs", headers=_headers(client)
    )
    assert resp.status_code == 200
    items = resp.get_json()["items"]
    assert len(items) == 2
