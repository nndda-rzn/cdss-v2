from app.core.exceptions.base import (
    AppException,
    AuthError,
    ConflictError,
    NotFoundError,
    ValidationError,
)


def test_auth_error_fields():
    err = AuthError(code="AUTH_INVALID_CREDENTIALS",
                    message_id="Email atau password salah",
                    message_en="Invalid email or password",
                    field="credentials")
    assert err.http_status == 401
    assert err.code == "AUTH_INVALID_CREDENTIALS"
    assert err.message_en == "Invalid email or password"

def test_status_codes():
    assert ValidationError(code="X", message_id="a", message_en="b").http_status == 422
    assert NotFoundError(code="X", message_id="a", message_en="b").http_status == 404
    assert ConflictError(code="X", message_id="a", message_en="b").http_status == 409
    assert isinstance(AuthError(code="X", message_id="a", message_en="b"), AppException)
