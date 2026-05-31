"""Path construction, study UID generation, and disk persistence for ECG images."""
import secrets
from datetime import UTC, datetime
from pathlib import Path


def generate_study_uid(facility_code: str) -> str:
    ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    rand = secrets.token_hex(2)  # 4 hex chars
    return f"ECG-{facility_code}-{ts}-{rand}"


def storage_path_for(
    *, facility_id: int, encounter_id: int, study_uid: str, ext: str
) -> str:
    """Relative path under the storage root."""
    return f"uploads/ecg/{facility_id}/{encounter_id}/{study_uid}.{ext}"


def save_image(storage_root: Path, relative_path: str, data: bytes) -> Path:
    """Write bytes to storage_root/relative_path, creating parent dirs."""
    target = storage_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target
