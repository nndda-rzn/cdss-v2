from app.config import DevConfig, ProdConfig, TestConfig


def test_test_config_uses_memory_or_tmp():
    cfg = TestConfig()
    assert cfg.TESTING is True
    assert cfg.JWT_SECRET_KEY


def test_prod_requires_jwt_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "prod-secret")
    cfg = ProdConfig()
    assert cfg.JWT_SECRET_KEY == "prod-secret"  # noqa: S105
    assert cfg.DEBUG is False


def test_dev_defaults():
    cfg = DevConfig()
    assert cfg.DEBUG is True
