"""Seed a clinician, nurse, researcher, or expert-reviewer user. Idempotent on email.

Entrypoint reads from env vars (CLINICIAN_ROLE/NAME/EMAIL/PASSWORD) for
non-interactive use (CI/Docker), or prompts interactively otherwise.
"""
import os
import sys
from getpass import getpass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security.password import hash_password
from app.db.models.user import User

_VALID_ROLES = frozenset({"clinician", "nurse", "researcher", "expert_reviewer"})


def seed_clinical_user(
    session: Session,
    *,
    name: str,
    email: str,
    password: str,
    facility_id: int,
    role: str,
    rounds: int = 12,
) -> User:
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


def _read_credentials() -> tuple[str, str, str, str]:
    env = os.environ
    if {
        "CLINICIAN_ROLE",
        "CLINICIAN_NAME",
        "CLINICIAN_EMAIL",
        "CLINICIAN_PASSWORD",
    } <= env.keys():
        return (
            env["CLINICIAN_ROLE"],
            env["CLINICIAN_NAME"],
            env["CLINICIAN_EMAIL"],
            env["CLINICIAN_PASSWORD"],
        )
    # Interactive prompt.
    if sys.stdin.isatty():
        print("Roles allowed: clinician, nurse, researcher, expert_reviewer")
        role = input("Role: ").strip().lower()
        name = input("Name: ")
        email = input("Email: ")
        password = getpass("Password: ")
        return role, name, email, password
    raise SystemExit(
        "Set CLINICIAN_ROLE/NAME/EMAIL/PASSWORD (non-interactive) or run in a terminal."
    )


if __name__ == "__main__":
    from app.db.engine import create_db_engine
    from app.db.models.facility import HealthcareFacility
    from app.paths import default_database_url

    role, name, email, password = _read_credentials()
    if role not in _VALID_ROLES:
        raise SystemExit(
            f"Invalid role '{role}'. Allowed: {', '.join(sorted(_VALID_ROLES))}"
        )
    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        facility = s.scalar(select(HealthcareFacility).order_by(HealthcareFacility.id))
        if facility is None:
            raise SystemExit("No facility found. Run seed_facility first.")
        seed_clinical_user(
            s,
            name=name,
            email=email,
            password=password,
            facility_id=facility.id,
            role=role,
        )
        s.commit()
    print(f"Seeded {role}: {email}", file=sys.stderr)
