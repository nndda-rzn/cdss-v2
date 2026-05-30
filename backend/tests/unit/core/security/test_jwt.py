from flask import Flask
from flask_jwt_extended import JWTManager, decode_token

from app.core.security.jwt import make_access_token


def test_access_token_carries_role_and_facility():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test"  # noqa: S105
    JWTManager(app)
    with app.app_context():
        token = make_access_token(user_id=1, role="admin", facility_id=7)
        decoded = decode_token(token)
        assert decoded["sub"] == "1"
        assert decoded["role"] == "admin"
        assert decoded["facility_id"] == 7
