"""Seed the first admin user. Idempotent on email.

Entrypoint reads from interactive prompt, falling back to env vars
ADMIN_EMAIL / ADMIN_PASSWORD / ADMIN_NAME for non-interactive (CI/Docker).
"""
import os
import sys
from getpass import getpass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security.password import hash_password
from app.db.models.user import User


def seed_admin(
    session: Session,
    *,
    name: str,
    email: str,
    password: str,
    facility_id: int,
    rounds: int = 12,
) -> User:
    existing = session.scalar(select(User).where(User.email == email))
    if existing is not None:
        return existing
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password, rounds=rounds),
        role="admin",
        facility_id=facility_id,
    )
    session.add(user)
    return user


def _read_credentials() -> tuple[str, str, str]:
    if sys.stdin.isatty():
        name = input("Admin name: ")
        email = input("Admin email: ")
        password = getpass("Admin password: ")
    else:
        name = os.environ["ADMIN_NAME"]
        email = os.environ["ADMIN_EMAIL"]
        password = os.environ["ADMIN_PASSWORD"]
    return name, email, password
