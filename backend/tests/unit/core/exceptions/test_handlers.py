from flask import Flask

from app.core.exceptions.base import AuthError
from app.core.exceptions.handlers import register_error_handlers


def _make_app():
    app = Flask(__name__)
    register_error_handlers(app)

    @app.get("/boom")
    def boom():
        raise AuthError(code="AUTH_INVALID_CREDENTIALS",
                        message_id="Email atau password salah",
                        message_en="Invalid email or password",
                        field="credentials")
    return app

def test_handler_maps_to_envelope():
    app = _make_app()
    client = app.test_client()
    resp = client.get("/boom")
    assert resp.status_code == 401
    body = resp.get_json()["error"]
    assert body["code"] == "AUTH_INVALID_CREDENTIALS"
    assert body["message_id"] == "Email atau password salah"
    assert body["message_en"] == "Invalid email or password"
    assert body["field"] == "credentials"
    assert "request_id" in body
