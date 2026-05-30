"""EKG-Insight backend application factory."""
from flask import Flask

from app.config import BaseConfig, DevConfig


def create_app(config: type[BaseConfig] = DevConfig) -> Flask:
    # Imports are local to the factory to avoid binding the name ``db`` as an
    # attribute of the ``app`` package, which would shadow the ``app/db/``
    # subpackage (flask-sqlalchemy's db instance vs the db module tree).
    from app.api import register_blueprints
    from app.core.encryption.fernet_provider import FernetProvider
    from app.core.encryption.hash_provider import HashProvider
    from app.core.encryption.key_loader import load_key
    from app.core.exceptions.handlers import register_error_handlers
    from app.core.logging.config import configure_logging
    from app.db.pragmas import register_sqlite_pragmas
    from app.db.types.context import set_crypto
    from app.extensions import db, jwt, migrate

    configure_logging()
    app = Flask(__name__, static_folder="static", static_url_path="/")
    app.config.from_object(config())

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if isinstance(uri, str) and uri.startswith("sqlite"):
        with app.app_context():
            register_sqlite_pragmas(db.engine)

    try:
        fernet = FernetProvider(load_key(app.config["MASTER_KEY_PATH"]))
        hasher = HashProvider(load_key(app.config["HMAC_PEPPER_PATH"]))
        set_crypto(fernet, hasher)
    except FileNotFoundError:
        if not app.config.get("TESTING"):
            raise

    register_error_handlers(app)
    register_blueprints(app)
    return app
