"""Login service: authenticate, audit, anti-enumeration generic error."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions.base import AuthError
from app.core.security.password import verify_password
from app.db.models.user import User
from app.services.audit.writer import write_audit

_INVALID: dict[str, str] = dict(
    code="AUTH_INVALID_CREDENTIALS",
    message_id="Email atau password salah",
    message_en="Invalid email or password",
    field="credentials",
)


def authenticate(session: Session, *, email: str, password: str,
                 ip_address: str, user_agent: str, request_id: str) -> User:
    user = session.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        write_audit(session, facility_id=(user.facility_id if user else None),
                    action="login_failed", user_id=(user.id if user else None),
                    ip_address=ip_address, user_agent=user_agent, request_id=request_id,
                    description=f"failed login for {email}")
        raise AuthError(**_INVALID)
    write_audit(session, facility_id=user.facility_id, action="login",
                user_id=user.id, ip_address=ip_address, user_agent=user_agent,
                request_id=request_id)
    return user
