"""Repository-root-anchored runtime paths.

Runtime artifacts (secrets, database) live at the repository root regardless
of the current working directory, matching the architecture overview. This
file is at ``backend/app/paths.py`` so ``parents[2]`` is the repo root.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = REPO_ROOT / "data"
SECRETS_DIR = REPO_ROOT / "secrets"
STORAGE_DIR = REPO_ROOT / "storage"

DEFAULT_DB_PATH = DATA_DIR / "cdss.db"
DEFAULT_MASTER_KEY_PATH = SECRETS_DIR / "master.key"
DEFAULT_HMAC_PEPPER_PATH = SECRETS_DIR / "hmac_pepper.key"


def default_database_url() -> str:
    return f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"
