from app import create_app
from app.config import TestConfig


def test_create_app_returns_flask_app():
    app = create_app(TestConfig)
    assert app is not None
    assert app.config["TESTING"] is True


def test_app_has_health_route():
    app = create_app(TestConfig)
    rules = {r.rule for r in app.url_map.iter_rules()}
    assert "/api/health" in rules
