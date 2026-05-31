"""Patient register API integration tests."""
import pytest
from sqlalchemy import select, text

from app.core.security.password import hash_password
from app.db.models.audit_log import AuditLog
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
                    id=i,
                    name=role,
                    email=email,
                    password_hash=hash_password("StrongPass1", rounds=4),
                    role=role,
                    facility_id=1,
                )
            )
        db.session.commit()
        yield app.test_client()


def _headers(client, role: str) -> dict[str, str]:
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


def test_register_patient_created(client):
    resp = client.post("/api/patients", json=_VALID, headers=_headers(client, "clinician"))
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["patient"]["mrn"] == "MRN-P1-000001"
    assert body["patient"]["nik_last4"] == "0001"


def test_register_without_nik(client):
    payload = {k: v for k, v in _VALID.items() if k != "nik"}
    resp = client.post("/api/patients", json=payload, headers=_headers(client, "nurse"))
    assert resp.status_code == 201


def test_register_duplicate_nik_409(client):
    client.post("/api/patients", json=_VALID, headers=_headers(client, "clinician"))
    dup = dict(_VALID, name="Lain Orang", dob="1970-01-01")
    resp = client.post(
        "/api/patients", json=dup, headers=_headers(client, "clinician")
    )
    assert resp.status_code == 409
    assert resp.get_json()["error"]["code"] == "PATIENT_NIK_DUPLICATE"


def test_register_forbidden_for_researcher(client):
    resp = client.post(
        "/api/patients", json=_VALID, headers=_headers(client, "researcher")
    )
    assert resp.status_code == 403


def test_register_forbidden_for_expert_reviewer(client):
    resp = client.post(
        "/api/patients", json=_VALID, headers=_headers(client, "expert_reviewer")
    )
    assert resp.status_code == 403


def test_register_writes_no_phi_access_log(client):
    client.post("/api/patients", json=_VALID, headers=_headers(client, "clinician"))
    assert db.session.scalar(select(PHIAccessLog)) is None


def test_register_writes_audit(client):
    client.post("/api/patients", json=_VALID, headers=_headers(client, "clinician"))
    row = db.session.scalar(
        select(AuditLog).where(AuditLog.action == "patient_register")
    )
    assert row is not None


def test_register_encryption_invariant(client):
    """AC-2: T1 fields stored encrypted; no plaintext in raw bytes."""
    client.post("/api/patients", json=_VALID, headers=_headers(client, "clinician"))
    row = db.session.execute(
        text(
            "SELECT name_encrypted, phone_encrypted, address_encrypted FROM patient"
        )
    ).one()
    raw = b"".join(bytes(v) for v in row if v is not None)
    assert b"Budi Santoso" not in raw
    assert b"0812345678" not in raw
    assert b"Jl. Mawar 5" not in raw


def test_register_dedup_suggestion(client):
    client.post("/api/patients", json=_VALID, headers=_headers(client, "clinician"))
    # Same name+dob+gender, no NIK -> dedup suggestion (200, not 201)
    similar = {
        "name": "Budi Santoso",
        "dob": "1965-03-12",
        "gender": "male",
        "consent_data_use": True,
    }
    resp = client.post(
        "/api/patients", json=similar, headers=_headers(client, "clinician")
    )
    assert resp.status_code == 200
    assert resp.get_json()["action"] == "confirm"
    assert len(resp.get_json()["duplicates"]) == 1


def test_register_confirm_new_skips_dedup(client):
    client.post("/api/patients", json=_VALID, headers=_headers(client, "clinician"))
    similar = {
        "name": "Budi Santoso",
        "dob": "1965-03-12",
        "gender": "male",
        "consent_data_use": True,
    }
    resp = client.post(
        "/api/patients?confirm_new=true",
        json=similar,
        headers=_headers(client, "clinician"),
    )
    assert resp.status_code == 201
