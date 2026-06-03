"""Orchestrator tests: run-all, partial failure, idempotency (mocked loader)."""
import uuid
from datetime import date

import pytest

from app.db.models.ai_analysis import AIAnalysis
from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.model_metadata import ModelMetadata
from app.db.models.patient import Patient
from app.services.inference import orchestrate
from app.services.inference.orchestrate import analyze_study


class _Probs:
    def __init__(self, data, top1):
        self.data = type("T", (), {"tolist": lambda self: data})()
        self.top1 = top1
        self.top1conf = data[top1]


class _Res:
    def __init__(self, data, top1):
        self.probs = _Probs(data, top1)


class _Model:
    """Fake YOLO model returning fixed probabilities."""

    def __init__(self, data, top1):
        self._r = _Res(data, top1)

    def predict(self, *a, **k):
        return [self._r]


class _RaisingModel:
    """Fake model whose .predict raises (simulates per-model failure)."""

    def predict(self, *a, **k):
        raise RuntimeError("inference exploded")


def _study(session) -> ECGStudy:
    p = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        name_encrypted="Budi", dob=date(1965, 3, 12), gender="male",
    )
    session.add(p)
    session.commit()
    e = Encounter(patient_id=p.id, facility_id=1, attending_user_id=1)
    session.add(e)
    session.commit()
    study = ECGStudy(
        encounter_id=e.id,
        patient_id=e.patient_id,
        study_uid="ECG-P1-20260531-abcd",
        image_original_path="uploads/ecg/1/1/ECG-P1-20260531-abcd.jpg",
        image_quality_status="good",
        image_quality_score=0.85,
        image_quality_metrics_json={},
        recorded_by_user_id=1,
    )
    session.add(study)
    session.commit()
    return study


def _models(session) -> list[ModelMetadata]:
    rows = [
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
    ]
    session.add_all(rows)
    session.commit()
    return rows


def test_run_all_creates_success_rows(
    session, seeded_admin, tmp_path, monkeypatch
):
    study = _study(session)
    _models(session)
    monkeypatch.setattr(
        orchestrate, "load_model",
        lambda path: _Model([0.1, 0.15, 0.7, 0.05], top1=2),
    )

    rows = analyze_study(
        session, study_id=study.id, user_id=1,
        model_dir=tmp_path / "models", storage_root=tmp_path / "storage",
    )

    assert len(rows) == 2
    assert all(r.status == "success" for r in rows)
    assert all(r.predicted_class == "mi" for r in rows)
    assert all(r.confidence_score == 0.7 for r in rows)
    assert all(r.device_used == "cpu" for r in rows)
    assert all(r.inference_time_ms is not None for r in rows)


def test_partial_failure(session, seeded_admin, tmp_path, monkeypatch):
    study = _study(session)
    models = _models(session)
    failing_path = str(tmp_path / "models" / models[1].model_file_path)

    def _fake_load(path):
        if path == failing_path:
            return _RaisingModel()
        return _Model([0.1, 0.15, 0.7, 0.05], top1=2)

    monkeypatch.setattr(orchestrate, "load_model", _fake_load)

    rows = analyze_study(
        session, study_id=study.id, user_id=1,
        model_dir=tmp_path / "models", storage_root=tmp_path / "storage",
    )

    by_model = {r.model_metadata_id: r for r in rows}
    assert by_model[models[0].id].status == "success"
    assert by_model[models[0].id].predicted_class == "mi"
    failed = by_model[models[1].id]
    assert failed.status == "failed"
    assert failed.predicted_class is None
    assert "inference exploded" in (failed.error_message or "")


def test_idempotent_rerun(session, seeded_admin, tmp_path, monkeypatch):
    study = _study(session)
    _models(session)
    monkeypatch.setattr(
        orchestrate, "load_model",
        lambda path: _Model([0.1, 0.15, 0.7, 0.05], top1=2),
    )

    first = analyze_study(
        session, study_id=study.id, user_id=1,
        model_dir=tmp_path / "models", storage_root=tmp_path / "storage",
    )
    first_ids = sorted(r.id for r in first)

    second = analyze_study(
        session, study_id=study.id, user_id=1,
        model_dir=tmp_path / "models", storage_root=tmp_path / "storage",
    )

    assert session.query(AIAnalysis).count() == 2
    assert len(second) == 2
    # Same physical rows preserved (no duplicate / delete-recreate).
    assert sorted(r.id for r in second) == first_ids
    assert all(r.status == "success" for r in second)


def test_study_not_found_raises(session, seeded_admin, tmp_path, monkeypatch):
    monkeypatch.setattr(
        orchestrate, "load_model",
        lambda path: _Model([0.1, 0.15, 0.7, 0.05], top1=2),
    )
    from app.core.exceptions.base import NotFoundError

    with pytest.raises(NotFoundError) as exc:
        analyze_study(
            session, study_id=99999, user_id=1,
            model_dir=tmp_path / "models", storage_root=tmp_path / "storage",
        )
    assert exc.value.code == "ECG_STUDY_NOT_FOUND"


def test_analyze_study_with_roi_crop(session, seeded_admin, tmp_path, monkeypatch):
    import os

    import numpy as np
    from PIL import Image

    study = _study(session)
    _models(session)

    # Create the storage directory and write a dummy ECG image
    img_dir = tmp_path / "storage" / os.path.dirname(study.image_original_path)
    img_dir.mkdir(parents=True, exist_ok=True)
    img_path = tmp_path / "storage" / study.image_original_path
    
    # Save a 100x100 RGB image
    arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    Image.fromarray(arr, mode="RGB").save(img_path)

    # Capture the image path passed to run_inference
    captured_paths = []
    def fake_run_inference(model, image_path, device="cpu"):
        captured_paths.append(image_path)
        return {
            "predicted_class": "mi",
            "confidence": 0.75,
            "probabilities": {
                "abnormal": 0.1, "homi": 0.1, "mi": 0.75, "normal": 0.05
            },
            "inference_ms": 12.5,
        }

    monkeypatch.setattr(
        orchestrate, "load_model",
        lambda path: _Model([0.1, 0.1, 0.75, 0.05], top1=2),
    )
    monkeypatch.setattr(orchestrate, "run_inference", fake_run_inference)

    rows = analyze_study(
        session, study_id=study.id, user_id=1,
        model_dir=tmp_path / "models", storage_root=tmp_path / "storage",
    )

    assert len(rows) == 2
    assert all(r.status == "success" for r in rows)
    # Check that we passed a temporary crop path, not the original path
    assert len(captured_paths) == 2
    for path in captured_paths:
        assert path != str(img_path)
        assert "ecg_crop_" in path
        # Check that the file existed when passed (though it is unlinked afterwards)
        assert not os.path.exists(path)  # Verify it was successfully cleaned up

