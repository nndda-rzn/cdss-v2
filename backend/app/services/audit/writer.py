"""Audit writer. Called explicitly from the service layer (not hidden middleware)."""
from sqlalchemy.orm import Session

from app.db.models.audit_log import AuditLog


def write_audit(
    session: Session,
    *,
    facility_id: int | None,
    action: str,
    user_id: int | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    description: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        facility_id=facility_id,
        action=action,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
    )
    session.add(entry)
    return entry
