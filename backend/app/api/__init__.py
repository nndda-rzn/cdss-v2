"""Blueprint registration."""
from flask import Flask


def register_blueprints(app: Flask) -> None:
    from app.api.auth import bp as auth_bp
    from app.api.health import bp as health_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
