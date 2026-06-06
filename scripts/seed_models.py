"""Seed ModelMetadata for trained YOLO classification models.

Primary: hardcoded 5-model list (deterministic).
Fallback: auto-discover *best.pt files in MODELS_DIR.
Idempotent on (model_name, model_version).
"""
import hashlib
import os
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.model_metadata import ModelMetadata

REPO_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = REPO_ROOT / "models"

# Primary: hardcoded trained models
_HARDCODED = {
    "yolov8n_cls": ("yolov8n-cls", "YOLOv8n"),
    "yolov8s_cls": ("yolov8s-cls", "YOLOv8s"),
    "yolo11n_cls": ("yolov11n-cls", "YOLOv11n"),
    "yolo11s_cls": ("yolov11s-cls", "YOLOv11s"),
    "yolo26n_cls": ("yolov26n-cls", "YOLOv26n"),
}
_ENUM_MAP = {
    "abnormal_heartbeat": "abnormal",
    "history_myocardial_infarction": "homi",
    "myocardial_infarction": "mi",
    "normal": "normal",
}
_CLASS_NAMES_DEFAULT = ["abnormal", "homi", "mi", "normal"]


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _exists(session: Session, name: str, version: str) -> bool:
    return session.scalar(
        select(ModelMetadata).where(
            ModelMetadata.model_name == name,
            ModelMetadata.model_version == version,
        )
    ) is not None


def _add_model(session: Session, *, name, arch, folder, weights, version, class_names, is_active=True):
    if _exists(session, name, version):
        return False
    size_mb = round(weights.stat().st_size / (1024 * 1024), 2)
    session.add(ModelMetadata(
        model_name=name,
        model_version=version,
        architecture=arch,
        task_type="classification",
        input_size=224,
        model_file_path=f"{folder}/{weights.name}",
        model_checksum=_sha256(weights),
        model_size_mb=size_mb,
        class_names_json=class_names,
        threshold_config_json={"confidence_threshold": 0.5},
        is_active=is_active,
    ))
    return True


def seed_models(session: Session, model_dir: Path = MODELS_DIR, version: str = "v1.0") -> int:
    """Register models: hardcoded list first, then auto-discover fallback."""
    count = 0

    # 1. Hardcoded models (if .pt files exist on disk)
    try:
        from ultralytics import YOLO
        for folder, (name, arch) in _HARDCODED.items():
            weights = model_dir / folder / "best.pt"
            if not weights.exists():
                print(f"skip {folder}: {weights} missing", file=sys.stderr)
                continue
            names = YOLO(str(weights)).names
            ordered = [_ENUM_MAP[names[i]] for i in sorted(names)]
            if _add_model(session, name=name, arch=arch, folder=folder,
                          weights=weights, version=version, class_names=ordered):
                count += 1
    except ImportError:
        print("ultralytics not installed, skipping hardcoded models", file=sys.stderr)

    # 2. Auto-discover fallback (Kaggle naming: *_best.pt)
    if not model_dir.exists():
        return count
    first = True
    for model_dir_entry in sorted(model_dir.iterdir()):
        if not model_dir_entry.is_dir():
            continue
        folder_name = model_dir_entry.name
        # Skip folders already handled by hardcoded list
        if folder_name in _HARDCODED:
            continue
        candidates = sorted(model_dir_entry.glob("*_best.pt")) + sorted(model_dir_entry.glob("best.pt"))
        if not candidates:
            continue
        best_pt = candidates[0]
        parts = folder_name.split("_")
        arch = parts[0] if parts else folder_name
        if _add_model(session, name=arch, arch=arch, folder=folder_name,
                      weights=best_pt, version=version,
                      class_names=_CLASS_NAMES_DEFAULT, is_active=first):
            count += 1
        first = False

    return count


if __name__ == "__main__":
    from app.db.engine import create_db_engine
    from app.paths import default_database_url

    model_dir = Path(os.environ.get("MODEL_DIR", str(MODELS_DIR)))
    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        n = seed_models(s, model_dir)
        s.commit()
    print(f"Models seeded: {n}", file=sys.stderr)
