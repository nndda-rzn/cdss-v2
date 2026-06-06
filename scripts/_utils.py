"""Shared utilities for seed scripts."""
import hashlib
import os
import sys
from getpass import getpass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security.password import hash_password
from app.db.models.user import User


def sha256_checksum(path, chunk_size=65536):
    """Compute SHA256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def prompt_or_env(prompt_text, env_key, *, required=True, secret=False):
    """Read from env var first, fall back to interactive prompt."""
    if env_key in os.environ:
        return os.environ[env_key]
    if sys.stdin.isatty():
        if secret:
            value = getpass(prompt_text) or None
        else:
            value = input(prompt_text) or None
        if value is None and required:
            raise SystemExit(f"Set {env_key} or provide a value interactively.")
        return value
    raise SystemExit(
        f"Set {env_key} (non-interactive) or run in a terminal."
    )


def seed_user(
    session: Session,
    *,
    name: str,
    email: str,
    password: str,
    facility_id: int,
    role: str,
    rounds: int = 12,
) -> User:
    """Create a user (idempotent on email)."""
    existing = session.scalar(select(User).where(User.email == email))
    if existing is not None:
        return existing
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password, rounds=rounds),
        role=role,
        facility_id=facility_id,
    )
    session.add(user)
    return user


def get_first_facility(session: Session):
    """Return the first HealthcareFacility or raise."""
    from app.db.models.facility import HealthcareFacility
    facility = session.scalar(select(HealthcareFacility).order_by(HealthcareFacility.id))
    if facility is None:
        raise SystemExit("No facility found. Run seed_facility first.")
    return facility
