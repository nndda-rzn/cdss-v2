"""ECGStudy API integration tests."""
import io

import cv2
import numpy as np
import pytest

from app.core.security.password import hash_password
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.extensions import db

_ROLES = {
    "clinician": "clinician@x.id",
    "nurse": "nurse@x.id",
    "researcher": "researcher@x.id",
}


def _real_jpeg() -> bytes:
    """A real, decodable JPEG (>1KB) so assess_quality's cv2.imdecode succeeds."""
    img = np.random.default_rng(0).integers(0, 256, (64, 64), dtype=np.uint8)
    ok, buf = cv2.imencode(".jpg", img)
    assert ok
    return buf.tobytes()


# A real JPEG (must be decodable by OpenCV for the quality check).
_JPEG = _real_jpeg()
# GIF is rejected on magic bytes before the quality check, so fake bytes are fine.
_GIF = b"GIF89a" + b"\x00" * 4096


@pytest.fixture()
def client(app, tmp_path, monkeypatch):
    app.config["STORAGE_DIR"] = str(tmp_path)
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


def _upload(client, encounter_id, data=_JPEG, filename="ecg.jpg",
            content_type="image/jpeg", role="clinician"):
    return client.post(
        f"/api/encounters/{encounter_id}/ecg-studies",
        data={"file": (io.BytesIO(data), filename, content_type)},
        content_type="multipart/form-data",
        headers=_headers(client, role),
    )


def test_upload_jpeg_201(client):
    e = _encounter(client)
    resp = _upload(client, e["id"])
    assert resp.status_code == 201
    body = resp.get_json()["study"]
    assert body["study_uid"].startswith("ECG-P1-")
    assert body["image_quality_status"] in ("good", "acceptable", "poor")
    assert set(body["image_quality_metrics_json"]) == {
        "blur", "noise", "brightness", "contrast"
    }


def test_upload_rejects_gif_422(client):
    e = _encounter(client)
    resp = _upload(client, e["id"], data=_GIF, filename="x.gif",
                   content_type="image/gif")
    assert resp.status_code == 422
    assert resp.get_json()["error"]["code"] == "INVALID_FILE_FORMAT"


def test_upload_rejects_too_large_422(client):
    e = _encounter(client)
    big = _JPEG + b"\x00" * (10 * 1024 * 1024 + 1)
    resp = _upload(client, e["id"], data=big)
    assert resp.status_code == 422
    assert resp.get_json()["error"]["code"] == "FILE_TOO_LARGE"


def test_upload_auto_captures_ai_consent(client):
    e = _encounter(client)
    resp = _upload(client, e["id"])
    assert resp.status_code == 201
    # A second upload still works (consent already given, no duplicate error).
    resp2 = _upload(client, e["id"])
    assert resp2.status_code == 201


def test_upload_blocked_when_consent_revoked(client):
    e = _encounter(client)
    # Revoke ai_analysis consent directly.
    import uuid
    from datetime import UTC, datetime

    from app.db.models.consent import Consent

    with client.application.app_context():
        db.session.add(Consent(
            patient_id=uuid.UUID(e["patient_id"]), consent_type="ai_analysis",
            status="revoked", revoked_at=datetime.now(UTC), recorded_by_user_id=1,
        ))
        db.session.commit()
    resp = _upload(client, e["id"])
    assert resp.status_code == 422
    assert resp.get_json()["error"]["code"] == "CONSENT_REVOKED"


def test_list_studies_desc(client):
    e = _encounter(client)
    _upload(client, e["id"])
    _upload(client, e["id"])
    resp = client.get(
        f"/api/encounters/{e['id']}/ecg-studies", headers=_headers(client)
    )
    assert resp.status_code == 200
    assert len(resp.get_json()["items"]) == 2


def test_researcher_gets_anonymized(client):
    e = _encounter(client)
    _upload(client, e["id"])
    resp = client.get(
        f"/api/encounters/{e['id']}/ecg-studies",
        headers=_headers(client, role="researcher"),
    )
    assert resp.status_code == 200
    item = resp.get_json()["items"][0]
    assert "patient_id" not in item
    assert "device_info" not in item


def test_upload_forbidden_for_researcher(client):
    e = _encounter(client)
    resp = _upload(client, e["id"], role="researcher")
    assert resp.status_code == 403
