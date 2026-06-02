"""Seed default system_config rows."""
from app.db.models.system_config import SystemConfig

DEFAULTS = [
    {"key": "enable_clinical_mode", "value_json": {"value": False}},
    {"key": "default_model_id", "value_json": {"value": None}},
    {"key": "nearest_pci_facility_distance_minutes", "value_json": {"value": 120}},
]


def seed_system_config(session) -> None:
    """Insert default system_config rows (idempotent)."""
    for entry in DEFAULTS:
        existing = session.get(SystemConfig, entry["key"])
        if existing is None:
            session.add(SystemConfig(key=entry["key"], value_json=entry["value_json"]))
