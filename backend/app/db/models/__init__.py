"""Import all models so Alembic autogenerate and create_all see them."""
from app.db.models.audit_log import AuditLog
from app.db.models.facility import HealthcareFacility
from app.db.models.phi_access_log import PHIAccessLog
from app.db.models.refresh_token import RefreshToken
from app.db.models.system_config import SystemConfig
from app.db.models.user import User

__all__ = [
    "HealthcareFacility",
    "User",
    "RefreshToken",
    "AuditLog",
    "PHIAccessLog",
    "SystemConfig",
]
