"""Admin API — user, facility, and system management (admin-only)."""
from flask import Blueprint

from app.api.admin.facilities import bp as facilities_bp
from app.api.admin.users import bp as users_bp

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
admin_bp.register_blueprint(users_bp)
admin_bp.register_blueprint(facilities_bp)
