"""Seed the first admin user. Idempotent on email.

Entrypoint reads from interactive prompt, falling back to env vars
ADMIN_EMAIL / ADMIN_PASSWORD / ADMIN_NAME for non-interactive (CI/Docker).
"""
import sys

from scripts._utils import get_first_facility, prompt_or_env, seed_user


def seed_admin(session, *, name, email, password, facility_id, rounds=12):
    """Seeded by seed_user with role='admin'."""
    return seed_user(
        session, name=name, email=email, password=password,
        facility_id=facility_id, role="admin", rounds=rounds,
    )


if __name__ == "__main__":
    from sqlalchemy.orm import Session
    from app.db.engine import create_db_engine
    from app.paths import default_database_url

    name = prompt_or_env("Admin name: ", "ADMIN_NAME")
    email = prompt_or_env("Admin email: ", "ADMIN_EMAIL")
    password = prompt_or_env("Admin password: ", "ADMIN_PASSWORD", secret=True)
    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        facility = get_first_facility(s)
        seed_admin(s, name=name, email=email, password=password, facility_id=facility.id)
        s.commit()
    print(f"Admin seeded: {email}", file=sys.stderr)
