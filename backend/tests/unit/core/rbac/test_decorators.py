from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from app.core.exceptions.handlers import register_error_handlers
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role


def _make_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test"  # noqa: S105
    JWTManager(app)
    register_error_handlers(app)

    @app.get("/admin-only")
    @require_role(Role.ADMIN)
    def admin_only():
        return {"ok": True}

    return app


def test_role_enum_values():
    assert Role.ADMIN.value == "admin"
    assert {r.value for r in Role} == {
        "admin", "clinical", "researcher"
    }


def test_decorator_blocks_wrong_role():
    app = _make_app()
    with app.app_context():
        token = create_access_token(identity="1", additional_claims={"role": "nurse"})
    client = app.test_client()
    resp = client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_decorator_allows_correct_role():
    app = _make_app()
    with app.app_context():
        token = create_access_token(identity="1", additional_claims={"role": "admin"})
    client = app.test_client()
    resp = client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
