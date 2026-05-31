"""Patient list/detail/update/delete API integration tests."""
import pytest
from sqlalchemy import select

from app.core.security.password import hash_password
from app.db.models.facility import HealthcareFacility
from app.db.models.phi_access_log import PHIAccessLog
from app.db.models.user import User
from app.extensions import db

_ROLES = {
    "admin": "admin@x.id",
    "clinician": "clinician@x.id",
    "nurse": "nurse@x.id",
    "researcher": "researcher@x.id",
    "expert_reviewer": "expert@x.id",
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


def _headers(client, role):
    resp = client.post(
        "/api/auth/login", json={"email": _ROLES[role], "password": "StrongPass1"}
    )
    return {"Authorization": f"Bearer {resp.get_json()['access_token']}"}


_VALID = {
    "name": "Budi Santoso",
    "dob": "1965-03-12",
    "gender": "male",
    "nik": "3201123456780001",
    "phone": "0812345678",
    "address": "Jl. Mawar 5",
    "consent_data_use": True,
}


def _register(client, role="clinician", **overrides):
    payload = dict(_VALID, **overrides)
    resp = client.post("/api/patients", json=payload, headers=_headers(client, role))
    return resp.get_json()["patient"]


def test_list_returns_masked_no_phi_log(client):
    _register(client)
    resp = client.get("/api/patients", headers=_headers(client, "clinician"))
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 1
    assert body["items"][0]["name_masked"] == "B*** S******"
    assert db.session.scalar(select(PHIAccessLog)) is None


def test_detail_returns_plaintext_with_phi_log(client):
    p = _register(client)
    resp = client.get(f"/api/patients/{p['id']}", headers=_headers(client, "clinician"))
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Budi Santoso"
    rows = db.session.scalars(select(PHIAccessLog)).all()
    assert {r.accessed_field for r in rows} == {"name", "phone", "address"}


def test_detail_researcher_gets_anonymized(client):
    p = _register(client)
    resp = client.get(
        f"/api/patients/{p['id']}", headers=_headers(client, "researcher")
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body.get("is_pseudonymized") is True
    assert "name" not in body


def test_update_patient(client):
    p = _register(client)
    resp = client.patch(
        f"/api/patients/{p['id']}",
        json={"phone": "0899999999"},
        headers=_headers(client, "clinician"),
    )
    assert resp.status_code == 200


def test_delete_by_admin(client):
    p = _register(client)
    resp = client.delete(
        f"/api/patients/{p['id']}",
        json={"reason": "duplikat"},
        headers=_headers(client, "admin"),
    )
    assert resp.status_code == 200
    listing = client.get("/api/patients", headers=_headers(client, "clinician"))
    assert listing.get_json()["total"] == 0


def test_delete_by_clinician_forbidden(client):
    p = _register(client)
    resp = client.delete(
        f"/api/patients/{p['id']}",
        json={"reason": "x"},
        headers=_headers(client, "clinician"),
    )
    assert resp.status_code == 403


def test_delete_without_reason_422(client):
    p = _register(client)
    resp = client.delete(
        f"/api/patients/{p['id']}",
        json={"reason": ""},
        headers=_headers(client, "admin"),
    )
    assert resp.status_code == 422
    assert resp.get_json()["error"]["code"] == "PATIENT_DELETE_REASON_REQUIRED"


def test_list_includes_deleted_for_admin(client):
    p = _register(client)
    client.delete(
        f"/api/patients/{p['id']}",
        json={"reason": "x"},
        headers=_headers(client, "admin"),
    )
    resp = client.get(
        "/api/patients?include_deleted=true", headers=_headers(client, "admin")
    )
    assert resp.get_json()["total"] == 1
