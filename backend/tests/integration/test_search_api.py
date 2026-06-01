"""Global search API integration tests."""
from typing import Any

import pytest
from flask.testing import FlaskClient

from app.core.security.password import hash_password
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.extensions import db

_ROLES = {"clinician": "clinician@x.id"}


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


def _headers(client: FlaskClient) -> dict[str, str]:
    resp = client.post(
        "/api/auth/login", json={"email": _ROLES["clinician"], "password": "StrongPass1"}
    )
    return {"Authorization": f"Bearer {resp.get_json()['access_token']}"}


def _make_patient(client: FlaskClient, name: str = "Budi Santoso") -> dict[str, Any]:
    body = client.post(
        "/api/patients?confirm_new=true",
        json={
            "name": name, "dob": "1965-03-12", "gender": "male",
            "consent_data_use": True,
        },
        headers=_headers(client),
    ).get_json()
    return body["patient"]  # type: ignore[no-any-return]


def test_search_empty_query_returns_empty(client):
    resp = client.get("/api/search?q=", headers=_headers(client))
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["patients"] == []
    assert body["encounters"] == []


def test_search_by_patient_mrn_prefix(client):
    p = _make_patient(client)
    mrn_prefix = p["mrn"][:6]

    resp = client.get(f"/api/search?q={mrn_prefix}", headers=_headers(client))
    body = resp.get_json()
    assert any(item["id"] == p["id"] for item in body["patients"])


def test_search_by_chief_complaint(client):
    p = _make_patient(client)
    client.post(
        "/api/encounters",
        json={"patient_id": p["id"], "chief_complaint": "Nyeri dada hebat"},
        headers=_headers(client),
    )

    resp = client.get("/api/search?q=nyeri", headers=_headers(client))
    body = resp.get_json()
    assert len(body["encounters"]) == 1
    assert "Nyeri" in body["encounters"][0]["chief_complaint"]


def test_search_requires_auth(client):
    resp = client.get("/api/search?q=test")
    assert resp.status_code == 401


def test_search_caps_results(client):
    """Result lists are bounded; the endpoint never returns more than 10 each."""
    for i in range(15):
        _make_patient(client, name=f"Pasien Demo {i:02d}")

    resp = client.get("/api/search?q=MRN", headers=_headers(client))
    body = resp.get_json()
    assert len(body["patients"]) <= 10
