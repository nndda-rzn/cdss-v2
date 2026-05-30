import pytest
from pydantic import ValidationError as PydanticError

from app.schemas.auth import LoginRequest, UserOut


def test_login_request_valid():
    req = LoginRequest(email="a@x.id", password="secret")  # noqa: S106
    assert req.email == "a@x.id"


def test_login_request_rejects_bad_email():
    with pytest.raises(PydanticError):
        LoginRequest(email="not-an-email", password="secret")  # noqa: S106


def test_user_out_serializes():
    out = UserOut(id=1, name="A", role="admin", facility_id=1)
    assert out.model_dump()["role"] == "admin"
