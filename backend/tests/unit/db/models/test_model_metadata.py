"""ModelMetadata model tests (registry of trained YOLO models)."""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models.model_metadata import ModelMetadata


def test_model_metadata_persists(session, seeded_admin):
    model = ModelMetadata(
        model_name="yolov8n-cls",
        model_version="v1.0",
        architecture="YOLOv8n",
        task_type="classification",
        input_size=224,
        model_file_path="yolov8n_cls/best.pt",
        model_checksum="abc",
        model_size_mb=2.83,
        class_names_json=["abnormal", "homi", "mi", "normal"],
        is_active=True,
    )
    session.add(model)
    session.commit()
    row = session.scalar(select(ModelMetadata))
    assert row is not None
    assert row.model_name == "yolov8n-cls"
    assert row.model_version == "v1.0"
    assert row.architecture == "YOLOv8n"
    assert row.task_type == "classification"
    assert row.input_size == 224
    assert row.model_file_path == "yolov8n_cls/best.pt"
    assert row.model_checksum == "abc"
    assert row.model_size_mb == 2.83
    assert row.class_names_json == ["abnormal", "homi", "mi", "normal"]
    assert row.is_active is True
    assert row.created_at is not None


def test_model_metadata_unique_name_version(session, seeded_admin):
    common = dict(
        architecture="YOLOv8n",
        task_type="classification",
        input_size=224,
        model_file_path="yolov8n_cls/best.pt",
        model_checksum="abc",
        model_size_mb=2.83,
        class_names_json=["abnormal", "homi", "mi", "normal"],
    )
    session.add(
        ModelMetadata(model_name="yolov8n-cls", model_version="v1.0", **common)
    )
    session.commit()
    session.add(
        ModelMetadata(model_name="yolov8n-cls", model_version="v1.0", **common)
    )
    with pytest.raises(IntegrityError):
        session.commit()
