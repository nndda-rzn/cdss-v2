import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_model_metadata import seed_model_metadata
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.model_metadata import ModelMetadata


def test_seed_creates_models(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.seed_model_metadata.MODELS_DIR", tmp_path)
    models_dir = tmp_path / "yolov8n_cls"
    models_dir.mkdir()
    (models_dir / "best.pt").write_bytes(b"fake-model-data")

    engine = create_engine(f"sqlite:///{tmp_path / 'models.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_model_metadata(s)
        s.commit()
        models = s.scalars(select(ModelMetadata)).all()
        assert len(models) == 1
        assert models[0].model_name == "yolov8n"
        assert models[0].is_active is True


def test_seed_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.seed_model_metadata.MODELS_DIR", tmp_path)
    models_dir = tmp_path / "yolov8n_cls"
    models_dir.mkdir()
    (models_dir / "best.pt").write_bytes(b"fake-model-data")

    engine = create_engine(f"sqlite:///{tmp_path / 'models2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_model_metadata(s)
        s.commit()
        seed_model_metadata(s)
        s.commit()
        count = s.scalar(select(func.count(ModelMetadata.id)))
        assert count == 1


def test_sets_only_first_as_active(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.seed_model_metadata.MODELS_DIR", tmp_path)
    for name in ["yolov8n_cls", "yolov8s_cls"]:
        d = tmp_path / name
        d.mkdir()
        (d / "best.pt").write_bytes(b"fake-model-data")

    engine = create_engine(f"sqlite:///{tmp_path / 'models3.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_model_metadata(s)
        s.commit()
        active = s.query(ModelMetadata).filter_by(is_active=True).all()
        assert len(active) == 1
