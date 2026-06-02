"""Unit tests for HiResCAM config_store DB CRUD."""
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.system_config import SystemConfig
from app.services.hirescam.config import HiResCAMConfig
from app.services.hirescam.config_store import CONFIG_KEY, get_config, save_config


def _make_session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    return Session(engine)


def _find_config(session):
    return session.scalar(
        select(SystemConfig).where(SystemConfig.key == CONFIG_KEY)
    )


class TestGetConfig:
    def test_returns_defaults_when_empty(self, tmp_path):
        s = _make_session(tmp_path)
        cfg = get_config(s)
        assert cfg == HiResCAMConfig()

    def test_reads_from_db(self, tmp_path):
        s = _make_session(tmp_path)
        s.add(SystemConfig(key=CONFIG_KEY, value_json=HiResCAMConfig(colormap="jet").to_dict()))
        s.commit()
        cfg = get_config(s)
        assert cfg.colormap == "jet"


class TestSaveConfig:
    def test_inserts_new(self, tmp_path):
        s = _make_session(tmp_path)
        cfg = HiResCAMConfig(smooth_sigma=2.0, colormap="turbo")
        save_config(s, cfg, user_id=1)
        s.commit()
        row = _find_config(s)
        assert row is not None
        assert row.value_json["smooth_sigma"] == 2.0
        assert row.updated_by == 1

    def test_updates_existing(self, tmp_path):
        s = _make_session(tmp_path)
        save_config(s, HiResCAMConfig(colormap="inferno"))
        s.commit()
        save_config(s, HiResCAMConfig(colormap="jet"), user_id=2)
        s.commit()
        row = _find_config(s)
        assert row.value_json["colormap"] == "jet"
        assert row.updated_by == 2

    def test_idempotent(self, tmp_path):
        s = _make_session(tmp_path)
        save_config(s, HiResCAMConfig())
        s.commit()
        save_config(s, HiResCAMConfig())
        s.commit()
        count = len(list(s.scalars(select(SystemConfig)).all()))
        assert count == 1
