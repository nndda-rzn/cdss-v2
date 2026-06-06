"""Seed a clinician, nurse, researcher, or expert-reviewer user. Idempotent on email."""
import sys

from scripts._utils import get_first_facility, prompt_or_env, seed_user

_VALID_ROLES = frozenset({"clinician", "nurse", "researcher", "expert_reviewer"})


def seed_clinical_user(session, *, name, email, password, facility_id, role, rounds=12):
    """Seeded by seed_user with the given role."""
    return seed_user(
        session, name=name, email=email, password=password,
        facility_id=facility_id, role=role, rounds=rounds,
    )


if __name__ == "__main__":
    from sqlalchemy.orm import Session
    from app.db.engine import create_db_engine
    from app.paths import default_database_url

    role = prompt_or_env("Role (clinician/nurse/researcher/expert_reviewer): ", "CLINICIAN_ROLE")
    if role not in _VALID_ROLES:
        raise SystemExit(f"Invalid role '{role}'. Allowed: {', '.join(sorted(_VALID_ROLES))}")
    name = prompt_or_env("Name: ", "CLINICIAN_NAME")
    email = prompt_or_env("Email: ", "CLINICIAN_EMAIL")
    password = prompt_or_env("Password: ", "CLINICIAN_PASSWORD", secret=True)
    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        facility = get_first_facility(s)
        seed_clinical_user(
            s, name=name, email=email, password=password,
            facility_id=facility.id, role=role,
        )
        s.commit()
    print(f"Seeded {role}: {email}", file=sys.stderr)
