"""AIAnalysis API integration tests (inference mocked at the loader boundary)."""
import io
import uuid
from datetime import UTC, datetime

import cv2
import numpy as np
import pytest

from app.core.security.password import hash_password
from app.db.models.ai_analysis import AIAnalysis
from app.db.models.consent import Consent
from app.db.models.facility import HealthcareFacility
from app.db.models.model_metadata import ModelMetadata
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


_JPEG = _real_jpeg()


# ---- Fake YOLO model (reuse the _Model/_Res/_Probs pattern from unit tests) ----
class _Probs:
    def __init__(self, data, top1):
        self.data = type("T", (), {"tolist": lambda self: data})()
        self.top1 = top1
        self.top1conf = data[top1]


class _Res:
    def __init__(self, data, top1):
        self.probs = _Probs(data, top1)


class _Model:
    """Fake YOLO model returning fixed probabilities (predicted_class=mi)."""

    def __init__(self, data, top1):
        self._r = _Res(data, top1)

    def predict(self, *a, **k):
        return [self._r]


def _fake_loader(path):
    return _Model([0.1, 0.15, 0.7, 0.05], top1=2)


@pytest.fixture()
def client(app, tmp_path, monkeypatch):
    app.config["STORAGE_DIR"] = str(tmp_path / "storage")
    app.config["MODEL_DIR"] = str(tmp_path / "models")
    monkeypatch.setattr(
        "app.services.inference.orchestrate.load_model", _fake_loader
    )
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
        db.session.add_all([
            ModelMetadata(
                model_name="yolov8n-cls", model_version="v1.0",
                architecture="YOLOv8n", task_type="classification",
                input_size=224, model_file_path="yolov8n_cls/best.pt",
                model_checksum="a", model_size_mb=2.83,
                class_names_json=["abnormal", "homi", "mi", "normal"],
                is_active=True,
            ),
            ModelMetadata(
                model_name="yolov8s-cls", model_version="v1.0",
                architecture="YOLOv8s", task_type="classification",
                input_size=224, model_file_path="yolov8s_cls/best.pt",
                model_checksum="b", model_size_mb=9.79,
                class_names_json=["abnormal", "homi", "mi", "normal"],
                is_active=True,
            ),
        ])
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


def _upload(client, encounter_id, role="clinician"):
    return client.post(
        f"/api/encounters/{encounter_id}/ecg-studies",
        data={"file": (io.BytesIO(_JPEG), "ecg.jpg", "image/jpeg")},
        content_type="multipart/form-data",
        headers=_headers(client, role),
    ).get_json()["study"]


def _analyze_url(encounter_id, study_id):
    return f"/api/encounters/{encounter_id}/ecg-studies/{study_id}/analyze"


def _analyses_url(encounter_id, study_id):
    return f"/api/encounters/{encounter_id}/ecg-studies/{study_id}/analyses"


def test_analyze_creates_rows(client):
    e = _encounter(client)
    s = _upload(client, e["id"])
    resp = client.post(
        _analyze_url(e["id"], s["id"]), headers=_headers(client)
    )
    assert resp.status_code == 201
    analyses = resp.get_json()["analyses"]
    assert len(analyses) == 2
    for a in analyses:
        assert a["predicted_class"] == "mi"
        assert a["model_name"]
        assert a["architecture"]
        assert a["status"] == "success"


def test_analyze_idempotent(client):
    e = _encounter(client)
    s = _upload(client, e["id"])
    first = client.post(_analyze_url(e["id"], s["id"]), headers=_headers(client))
    assert first.status_code == 201
    assert len(first.get_json()["analyses"]) == 2

    second = client.post(_analyze_url(e["id"], s["id"]), headers=_headers(client))
    assert second.status_code == 201
    assert len(second.get_json()["analyses"]) == 2

    with client.application.app_context():
        assert db.session.query(AIAnalysis).count() == 2


def test_analyze_consent_revoked_422(client):
    e = _encounter(client)
    s = _upload(client, e["id"])
    # Upload auto-captured ai_analysis consent; insert a later revoke (latest wins).
    with client.application.app_context():
        db.session.add(Consent(
            patient_id=uuid.UUID(e["patient_id"]), consent_type="ai_analysis",
            status="revoked", revoked_at=datetime.now(UTC), recorded_by_user_id=1,
        ))
        db.session.commit()
    resp = client.post(_analyze_url(e["id"], s["id"]), headers=_headers(client))
    assert resp.status_code == 422
    assert resp.get_json()["error"]["code"] == "CONSENT_REVOKED"


def test_analyze_forbidden_researcher(client):
    e = _encounter(client)
    s = _upload(client, e["id"])
    resp = client.post(
        _analyze_url(e["id"], s["id"]), headers=_headers(client, role="researcher")
    )
    assert resp.status_code == 403


def test_get_analyses_ordered(client):
    e = _encounter(client)
    s = _upload(client, e["id"])
    client.post(_analyze_url(e["id"], s["id"]), headers=_headers(client))
    resp = client.get(_analyses_url(e["id"], s["id"]), headers=_headers(client))
    assert resp.status_code == 200
    items = resp.get_json()["items"]
    assert len(items) == 2
    ids = [it["model_metadata_id"] for it in items]
    assert ids == sorted(ids)


def test_get_analyses_researcher_ok(client):
    e = _encounter(client)
    s = _upload(client, e["id"])
    client.post(_analyze_url(e["id"], s["id"]), headers=_headers(client))
    resp = client.get(
        _analyses_url(e["id"], s["id"]), headers=_headers(client, role="researcher")
    )
    assert resp.status_code == 200
    assert len(resp.get_json()["items"]) == 2
