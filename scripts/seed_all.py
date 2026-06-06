"""Orchestrate all seeders in dependency order.

Usage:
  python -m scripts.seed_all                    # interactive
  python -m scripts.seed_all --admin-only       # admin + facility only
  FACILITY_NAME=Puskesmas X python -m scripts.seed_all  # env vars
"""
import argparse
import sys

from sqlalchemy.orm import Session

from app.db.engine import create_db_engine
from app.paths import default_database_url


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed all data in order")
    parser.add_argument("--admin-only", action="store_true", help="Only seed facility + admin")
    args = parser.parse_args()

    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        # 1. Facility (required by all users)
        from scripts.seed_facility import seed_facility
        from scripts._utils import prompt_or_env

        print("=== Facility ===", file=sys.stderr)
        name = prompt_or_env("Facility name: ", "FACILITY_NAME")
        code = prompt_or_env("Facility code: ", "FACILITY_CODE")
        ftype = prompt_or_env("Facility type: ", "FACILITY_TYPE")
        address = prompt_or_env("Address (optional): ", "FACILITY_ADDRESS", required=False)
        fac = seed_facility(s, name=name, code=code, facility_type=ftype, address=address)
        s.commit()
        print(f"Facility ready: {fac.code}", file=sys.stderr)

        # 2. Admin
        from scripts.seed_admin import seed_admin
        print("\n=== Admin ===", file=sys.stderr)
        a_name = prompt_or_env("Admin name: ", "ADMIN_NAME")
        a_email = prompt_or_env("Admin email: ", "ADMIN_EMAIL")
        a_pass = prompt_or_env("Admin password: ", "ADMIN_PASSWORD", secret=True)
        seed_admin(s, name=a_name, email=a_email, password=a_pass, facility_id=fac.id)
        s.commit()
        print(f"Admin ready: {a_email}", file=sys.stderr)

        if args.admin_only:
            print("Done (admin-only mode).", file=sys.stderr)
            return

        # 3. Clinician
        from scripts.seed_clinician import seed_clinical_user, _VALID_ROLES
        print("\n=== Clinical User ===", file=sys.stderr)
        role = prompt_or_env("Role: ", "CLINICIAN_ROLE")
        if role not in _VALID_ROLES:
            raise SystemExit(f"Invalid role '{role}'.")
        c_name = prompt_or_env("Name: ", "CLINICIAN_NAME")
        c_email = prompt_or_env("Email: ", "CLINICIAN_EMAIL")
        c_pass = prompt_or_env("Password: ", "CLINICIAN_PASSWORD", secret=True)
        seed_clinical_user(
            s, name=c_name, email=c_email, password=c_pass,
            facility_id=fac.id, role=role,
        )
        s.commit()
        print(f"Clinical user ready: {role} {c_email}", file=sys.stderr)

        # 4. System config
        from scripts.seed_system_config import seed_system_config
        print("\n=== System Config ===", file=sys.stderr)
        seed_system_config(s)
        s.commit()
        print("System config ready.", file=sys.stderr)

        # 5. Models
        from scripts.seed_models import seed_models
        print("\n=== Models ===", file=sys.stderr)
        n = seed_models(s)
        s.commit()
        print(f"Models ready: {n} seeded.", file=sys.stderr)

    print("\nAll seeders complete.", file=sys.stderr)


if __name__ == "__main__":
    main()
