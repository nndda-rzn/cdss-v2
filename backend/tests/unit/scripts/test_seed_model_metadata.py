import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_models import seed_models
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.model_metadata import ModelMetadata


def test_seed_creates_models(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "ultralytics", None)
    models_dir = tmp_path / "custom_cls"
    models_dir.mkdir()
    (models_dir / "best.pt").write_bytes(b"fake-model-data")

    engine = create_engine(f"sqlite:///{tmp_path / 'models.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_models(s, model_dir=tmp_path)
        s.commit()
        models = s.scalars(select(ModelMetadata)).all()
        assert len(models) == 1
        assert models[0].model_name == "custom"
        assert models[0].is_active is True


def test_seed_idempotent(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "ultralytics", None)
    models_dir = tmp_path / "custom_cls"
    models_dir.mkdir()
    (models_dir / "best.pt").write_bytes(b"fake-model-data")

    engine = create_engine(f"sqlite:///{tmp_path / 'models2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_models(s, model_dir=tmp_path)
        s.commit()
        seed_models(s, model_dir=tmp_path)
        s.commit()
        count = s.scalar(select(func.count(ModelMetadata.id)))
        assert count == 1


def test_sets_only_first_as_active(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "ultralytics", None)
    for name in ["custom_a", "custom_b"]:
        d = tmp_path / name
        d.mkdir()
        (d / "best.pt").write_bytes(b"fake-model-data")

    engine = create_engine(f"sqlite:///{tmp_path / 'models3.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_models(s, model_dir=tmp_path)
        s.commit()
        active = s.query(ModelMetadata).filter_by(is_active=True).all()
        assert len(active) == 1


def test_seed_kaggle_naming(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "ultralytics", None)
    models_dir = tmp_path / "custom_kaggle"
    models_dir.mkdir()
    (models_dir / "custom_kaggle_ecg_roi_best.pt").write_bytes(b"fake-model-data")

    engine = create_engine(f"sqlite:///{tmp_path / 'kaggle.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_models(s, model_dir=tmp_path)
        s.commit()
        models = s.scalars(select(ModelMetadata)).all()
        assert len(models) == 1
        assert models[0].model_name == "custom"
        assert models[0].model_file_path == "custom_kaggle/custom_kaggle_ecg_roi_best.pt"


def test_best_pt_takes_fallback(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "ultralytics", None)
    models_dir = tmp_path / "custom_cls"
    models_dir.mkdir()
    (models_dir / "best.pt").write_bytes(b"fallback-model")

    engine = create_engine(f"sqlite:///{tmp_path / 'fallback.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_models(s, model_dir=tmp_path)
        s.commit()
        models = s.scalars(select(ModelMetadata)).all()
        assert len(models) == 1
        assert models[0].model_file_path == "custom_cls/best.pt"
