"""Application configuration."""
import os
from datetime import timedelta

from app.paths import (
    DEFAULT_HMAC_PEPPER_PATH,
    DEFAULT_MASTER_KEY_PATH,
    MODEL_DIR,
    STORAGE_DIR,
    default_database_url,
)

_DEV_JWT_KEY = "dev-only-change-me"  # noqa: S105


class BaseConfig:
    def __init__(self) -> None:
        self.JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", _DEV_JWT_KEY)
        self.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
        self.REFRESH_TTL_DAYS = 7
        self.LOGIN_RATE_LIMIT_MAX = int(os.environ.get("LOGIN_RATE_LIMIT_MAX", "5"))
        self.LOGIN_RATE_LIMIT_WINDOW = int(os.environ.get("LOGIN_RATE_LIMIT_WINDOW", "300"))
        self.SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", default_database_url())
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.MASTER_KEY_PATH = os.environ.get("MASTER_KEY_PATH", str(DEFAULT_MASTER_KEY_PATH))
        self.HMAC_PEPPER_PATH = os.environ.get("HMAC_PEPPER_PATH", str(DEFAULT_HMAC_PEPPER_PATH))
        self.STORAGE_DIR = os.environ.get("STORAGE_DIR", str(STORAGE_DIR))
        self.MODEL_DIR = os.environ.get("MODEL_DIR", str(MODEL_DIR))
        self.APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")
        self.GIT_SHA = os.environ.get("GIT_SHA", "local")
        self.DEBUG = False
        self.TESTING = False


class DevConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.DEBUG = True


class ProdConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.DEBUG = False
        # Never serve production traffic with the publicly-known dev key (I4).
        if self.JWT_SECRET_KEY == _DEV_JWT_KEY:
            raise RuntimeError(
                "JWT_SECRET_KEY must be set to a non-default value in production"
            )


class TestConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        self.JWT_SECRET_KEY = "test-secret"  # noqa: S105
        self.STORAGE_DIR = os.environ.get("TEST_STORAGE_DIR", str(STORAGE_DIR / "_test"))
        self.MODEL_DIR = os.environ.get("TEST_MODEL_DIR", str(MODEL_DIR))
