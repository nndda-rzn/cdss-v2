"""WSGI entrypoint.

Selects the config from FLASK_ENV (development -> DevConfig, production ->
ProdConfig). Flask's ``--app wsgi`` discovers the ``app`` object below, and
``flask db`` discovers the same app for migrations.
"""
import os

from app import create_app
from app.config import DevConfig, ProdConfig

_env = os.environ.get("FLASK_ENV", "development").lower()
_config = ProdConfig if _env == "production" else DevConfig

app = create_app(_config)
