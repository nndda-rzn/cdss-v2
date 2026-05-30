"""Application configuration."""
import os
from datetime import timedelta


class BaseConfig:
    def __init__(self) -> None:
        self.JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me")  # noqa: S105
        self.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
        self.REFRESH_TTL_DAYS = 7
        self.SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///data/cdss.db")
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.MASTER_KEY_PATH = os.environ.get("MASTER_KEY_PATH", "secrets/master.key")
        self.HMAC_PEPPER_PATH = os.environ.get("HMAC_PEPPER_PATH", "secrets/hmac_pepper.key")
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


class TestConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        self.JWT_SECRET_KEY = "test-secret"  # noqa: S105
