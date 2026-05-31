"""Cache loaded YOLO models by resolved path (avoid reloading per request)."""
from functools import lru_cache
from pathlib import Path
from typing import Any


@lru_cache(maxsize=8)
def load_model(resolved_path: str) -> Any:
    from ultralytics import YOLO

    if not Path(resolved_path).exists():
        raise FileNotFoundError(f"Model weights not found: {resolved_path}")
    return YOLO(resolved_path)
