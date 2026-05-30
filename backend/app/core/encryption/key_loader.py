"""Load cryptographic keys from disk."""
from pathlib import Path


def load_key(path: str) -> bytes:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Key file not found: {path}")
    return p.read_bytes()
