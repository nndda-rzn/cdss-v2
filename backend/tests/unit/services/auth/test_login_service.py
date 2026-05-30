import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.exceptions.base import AuthError
from app.core.security.password import hash_password
from app.db.base import Base
from app.db.models.audit_log import AuditLog
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User
from app.services.auth.login_service import authenticate


def _seed(engine):
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(User(id=1, name="A", email="a@x.id",
                   password_hash=hash_password("good", rounds=4),
                   role="admin", facility_id=1))
        s.commit()


def test_authenticate_success(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'login.db'}")
    Base.metadata.create_all(engine)
    _seed(engine)
    with Session(engine) as s:
        user = authenticate(s, email="a@x.id", password="good",  # noqa: S106
                            ip_address="127.0.0.1", user_agent="pytest", request_id="r1")
        s.commit()
        assert user.id == 1
        assert s.query(AuditLog).filter_by(action="login").count() == 1


def test_authenticate_wrong_password_generic(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'login2.db'}")
    Base.metadata.create_all(engine)
    _seed(engine)
    with Session(engine) as s:
        with pytest.raises(AuthError) as exc:
            authenticate(s, email="a@x.id", password="bad",  # noqa: S106
                         ip_address="127.0.0.1", user_agent="pytest", request_id="r2")
        assert exc.value.code == "AUTH_INVALID_CREDENTIALS"
        s.commit()
        assert s.query(AuditLog).filter_by(action="login_failed").count() == 1


def test_authenticate_unknown_email_same_error(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'login3.db'}")
    Base.metadata.create_all(engine)
    _seed(engine)
    with Session(engine) as s:
        with pytest.raises(AuthError) as exc:
            authenticate(s, email="nobody@x.id", password="x",  # noqa: S106
                         ip_address="127.0.0.1", user_agent="pytest", request_id="r3")
        assert exc.value.code == "AUTH_INVALID_CREDENTIALS"
