import os
import sqlite3
import subprocess
from pathlib import Path


def test_upgrade_then_downgrade(tmp_path: Path):
    db = tmp_path / "mig.db"
    full_env = {**os.environ, "DATABASE_URL": f"sqlite:///{db}"}
    up = subprocess.run(["alembic", "upgrade", "head"], cwd=".", env=full_env)  # noqa: S607
    assert up.returncode == 0
    # A real migration must have been applied.
    conn = sqlite3.connect(db)
    try:
        rows = conn.execute("SELECT version_num FROM alembic_version").fetchall()
    finally:
        conn.close()
    assert rows, "no migration was applied"
    down = subprocess.run(["alembic", "downgrade", "base"], cwd=".", env=full_env)  # noqa: S607
    assert down.returncode == 0
