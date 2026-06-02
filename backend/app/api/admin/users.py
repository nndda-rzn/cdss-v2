"""Admin user management endpoints."""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.api._shared import session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.core.security.password import hash_password
from app.db.models.user import User

bp = Blueprint("admin_users", __name__, url_prefix="/users")


@bp.get("")
@require_role(Role.ADMIN)
def list_users():
    users = session().query(User).order_by(User.id).all()
    items = [
        {
            "id": u.id, "name": u.name, "email": u.email, "role": u.role,
            "facility_id": u.facility_id, "is_active": u.is_active,
            "profession": u.profession, "license_number": u.license_number,
        }
        for u in users
    ]
    return jsonify(items=items)


@bp.post("")
@require_role(Role.ADMIN)
def create_user():
    data = request.get_json() or {}
    required = ["name", "email", "password", "role", "facility_id"]
    missing = [k for k in required if k not in data]
    if missing:
        abort(400, description=f"Missing: {', '.join(missing)}")

    user = User(
        name=data["name"],
        email=data["email"],
        password_hash=hash_password(data["password"]),
        role=data["role"],
        facility_id=data["facility_id"],
        profession=data.get("profession"),
        license_number=data.get("license_number"),
    )
    session().add(user)
    try:
        session().commit()
    except IntegrityError:
        session().rollback()
        abort(409, description="Email already exists")
    return jsonify(
        id=user.id, name=user.name, email=user.email, role=user.role,
        facility_id=user.facility_id, is_active=user.is_active,
    ), 201


@bp.put("/<int:user_id>")
@require_role(Role.ADMIN)
def update_user(user_id: int):
    user = session().get(User, user_id)
    if user is None:
        abort(404, description="User not found")
    data = request.get_json() or {}
    if "name" in data:
        user.name = data["name"]
    if "role" in data:
        user.role = data["role"]
    if "facility_id" in data:
        user.facility_id = data["facility_id"]
    if "is_active" in data:
        user.is_active = data["is_active"]
    if "profession" in data:
        user.profession = data["profession"]
    if "license_number" in data:
        user.license_number = data["license_number"]
    if "password" in data:
        user.password_hash = hash_password(data["password"])
    session().commit()
    return jsonify(
        id=user.id, name=user.name, email=user.email, role=user.role,
        facility_id=user.facility_id, is_active=user.is_active,
    )
