"""Seed the 5 trained YOLO classification models into ModelMetadata."""
import hashlib
import os
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.model_metadata import ModelMetadata

_FOLDERS = {
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


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def seed_models(session: Session, model_dir: Path, version: str = "v1.0") -> int:
    from ultralytics import YOLO

    count = 0
    for folder, (name, arch) in _FOLDERS.items():
        weights = model_dir / folder / "best.pt"
        if not weights.exists():
            print(f"skip {folder}: {weights} missing", file=sys.stderr)
            continue
        exists = session.scalar(
            select(ModelMetadata).where(
                ModelMetadata.model_name == name,
                ModelMetadata.model_version == version,
            )
        )
        if exists is not None:
            continue
        names = YOLO(str(weights)).names
        ordered = [_ENUM_MAP[names[i]] for i in sorted(names)]
        session.add(
            ModelMetadata(
                model_name=name,
                model_version=version,
                architecture=arch,
                task_type="classification",
                input_size=224,
                model_file_path=f"{folder}/best.pt",
                model_checksum=_sha256(weights),
                model_size_mb=round(weights.stat().st_size / (1024 * 1024), 2),
                class_names_json=ordered,
                threshold_config_json={},
                is_active=True,
            )
        )
        count += 1
    return count


if __name__ == "__main__":
    from app.db.engine import create_db_engine
    from app.paths import default_database_url

    model_dir = Path(os.environ.get("MODEL_DIR", "models"))
    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        n = seed_models(s, model_dir)
        s.commit()
    print(f"Models seeded: {n}", file=sys.stderr)
