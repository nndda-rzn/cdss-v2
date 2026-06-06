"""Seed ModelMetadata by auto-discovering *.pt files in MODELS_DIR.

Scans each subfolder for *_best.pt or best.pt files.
Reads class names from YOLO weights when ultralytics is available.
First discovered model is marked active.
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


def _read_class_names(weights_path: Path) -> list[str]:
    """Try reading class names from YOLO weights, fallback to default."""
    try:
        from ultralytics import YOLO
        names = YOLO(str(weights_path)).names
        return [names[i] for i in sorted(names)]
    except Exception:
        return list(_CLASS_NAMES_DEFAULT)


def _derive_architecture(folder_name: str) -> str:
    """Extract architecture name from folder name (e.g. yolov8n_cls -> yolov8n)."""
    parts = folder_name.split("_")
    return parts[0] if parts else folder_name


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
    """Discover and register all models from model_dir subfolders."""
    if not model_dir.exists():
        print(f"Model dir {model_dir} not found, skipping.", file=sys.stderr)
        return 0

    count = 0
    first = True
    for entry in sorted(model_dir.iterdir()):
        if not entry.is_dir():
            continue
        folder_name = entry.name
        candidates = sorted(entry.glob("*_best.pt")) + sorted(entry.glob("best.pt"))
        if not candidates:
            continue
        best_pt = candidates[0]
        arch = _derive_architecture(folder_name)
        class_names = _read_class_names(best_pt)
        if _add_model(
            session, name=folder_name, arch=arch, folder=folder_name,
            weights=best_pt, version=version, class_names=class_names,
            is_active=first,
        ):
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
