"""Seed model_metadata from files on disk.

Scans MODELS_DIR for subdirectories containing `best.pt`, registers each
as a ModelMetadata row. Idempotent on (model_name, model_version).
"""
import hashlib
from pathlib import Path

from sqlalchemy import select

from app.db.models.model_metadata import ModelMetadata

REPO_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = REPO_ROOT / "models"


def _file_checksum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def seed_model_metadata(session) -> None:
    """Register all models from disk (idempotent)."""
    if not MODELS_DIR.exists():
        return

    first = True
    for model_dir in sorted(MODELS_DIR.iterdir()):
        best_pt = model_dir / "best.pt"
        if not model_dir.is_dir() or not best_pt.exists():
            continue

        folder_name = model_dir.name
        parts = folder_name.split("_")
        arch = parts[0] if parts else folder_name
        version = "1.0"

        existing = session.scalar(
            select(ModelMetadata).where(
                ModelMetadata.model_name == arch,
                ModelMetadata.model_version == version,
            )
        )
        if existing is not None:
            continue

        size_mb = round(best_pt.stat().st_size / (1024 * 1024), 2)

        model = ModelMetadata(
            model_name=arch,
            model_version=version,
            architecture=arch,
            task_type="classification",
            input_size=224,
            model_file_path=f"{folder_name}/best.pt",
            model_checksum=_file_checksum(best_pt),
            model_size_mb=size_mb,
            class_names_json=["abnormal", "homi", "mi", "normal"],
            threshold_config_json={"confidence_threshold": 0.5},
            is_active=first,
        )
        session.add(model)
        first = False


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(REPO_ROOT.parent))
    from app import create_app
    from app.extensions import db

    app = create_app()
    with app.app_context():
        seed_model_metadata(db.session)
        db.session.commit()
        print("Models seeded.")
