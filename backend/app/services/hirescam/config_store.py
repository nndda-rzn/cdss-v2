"""CRUD helpers for HiResCAM config stored in system_config table."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.system_config import SystemConfig
from app.services.hirescam.config import HiResCAMConfig

CONFIG_KEY = "hirescam_config"


def _find(session: Session) -> SystemConfig | None:
    """Find the hirescam_config row."""
    return session.scalar(
        select(SystemConfig).where(SystemConfig.key == CONFIG_KEY)
    )


def get_config(session: Session) -> HiResCAMConfig:
    """Read active HiResCAM config from DB, return defaults if missing."""
    row = _find(session)
    if row is None:
        return HiResCAMConfig()
    return HiResCAMConfig.from_dict(row.value_json)


def save_config(
    session: Session,
    config: HiResCAMConfig,
    *,
    user_id: int | None = None,
) -> None:
    """Upsert HiResCAM config into system_config table."""
    row = _find(session)
    if row is None:
        row = SystemConfig(
            key=CONFIG_KEY,
            value_json=config.to_dict(),
            updated_by=user_id,
        )
        session.add(row)
    else:
        row.value_json = config.to_dict()
        row.updated_by = user_id
