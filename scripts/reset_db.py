"""Reset database: drop → migrate → seed. Clears storage uploads (keeps models/)."""
import os
import sys
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
DB_PATH = DATA_DIR / "cdss.db"
STORAGE_DIR = REPO_ROOT / "storage"


def reset_database():
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Deleted {DB_PATH}", file=sys.stderr)
    DATA_DIR.mkdir(exist_ok=True)
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(REPO_ROOT / "backend"),
        check=True,
    )
    print("Migrations applied.", file=sys.stderr)


def reset_storage():
    for sub in ["uploads", "heatmaps", "reports", "processed"]:
        d = STORAGE_DIR / sub
        if d.exists():
            shutil.rmtree(d)
            print(f"Cleared {d}", file=sys.stderr)
    STORAGE_DIR.mkdir(exist_ok=True)
    (STORAGE_DIR / "uploads" / "ecg").mkdir(parents=True, exist_ok=True)


def seed():
    env = os.environ.copy()
    env.setdefault("FACILITY_NAME", "Puskesmas Contoh")
    env.setdefault("FACILITY_CODE", "PUSK-001")
    env.setdefault("FACILITY_TYPE", "puskesmas")
    env.setdefault("ADMIN_NAME", "Admin")
    env.setdefault("ADMIN_EMAIL", "admin@cdss.id")
    env.setdefault("ADMIN_PASSWORD", "StrongPass1")
    env.setdefault("CLINICIAN_ROLE", "clinical")
    env.setdefault("CLINICIAN_NAME", "Dr. Contoh")
    env.setdefault("CLINICIAN_EMAIL", "clinician@cdss.id")
    env.setdefault("CLINICIAN_PASSWORD", "StrongPass1")

    subprocess.run(
        [sys.executable, "-m", "scripts.seed_all", "--admin-only"],
        cwd=str(REPO_ROOT), env=env, check=True,
    )
    print("Seeded: facility + admin.", file=sys.stderr)

    subprocess.run(
        [sys.executable, "-m", "scripts.seed_clinician"],
        cwd=str(REPO_ROOT), env=env, check=True,
    )
    print("Seeded: clinical user.", file=sys.stderr)


if __name__ == "__main__":
    print("=== Resetting database ===", file=sys.stderr)
    reset_database()
    reset_storage()
    seed()
    print("\n=== Done. ===", file=sys.stderr)
