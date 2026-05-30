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
    env = os.environ
    if {"ADMIN_NAME", "ADMIN_EMAIL", "ADMIN_PASSWORD"} <= env.keys():
        return env["ADMIN_NAME"], env["ADMIN_EMAIL"], env["ADMIN_PASSWORD"]
    if sys.stdin.isatty():
        name = input("Admin name: ")
        email = input("Admin email: ")
        password = getpass("Admin password: ")
        return name, email, password
    raise SystemExit(
        "Set ADMIN_NAME/ADMIN_EMAIL/ADMIN_PASSWORD (non-interactive) or run in a terminal."
    )


if __name__ == "__main__":
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from app.db.engine import create_db_engine
    from app.db.models.facility import HealthcareFacility
    from app.paths import default_database_url

    name, email, password = _read_credentials()
    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        facility = s.scalar(select(HealthcareFacility).order_by(HealthcareFacility.id))
        if facility is None:
            raise SystemExit("No facility found. Run seed_facility first.")
        seed_admin(
            s, name=name, email=email, password=password, facility_id=facility.id
        )
        s.commit()
    print(f"Admin seeded: {email}", file=sys.stderr)
