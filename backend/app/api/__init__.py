"""Blueprint registration."""
from flask import Flask


def register_blueprints(app: Flask) -> None:
    from app.api.auth import bp as auth_bp
    from app.api.health import bp as health_bp
    from app.api.patients import bp as patients_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
