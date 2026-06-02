"""Admin facility management endpoints."""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.api._shared import session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.facility import HealthcareFacility

bp = Blueprint("admin_facilities", __name__, url_prefix="/facilities")


@bp.get("")
@require_role(Role.ADMIN)
def list_facilities():
    facs = session().query(HealthcareFacility).order_by(HealthcareFacility.id).all()
    items = [
        {
            "id": f.id, "name": f.name, "code": f.code,
            "facility_type": f.facility_type, "address": f.address,
            "province_code": f.province_code, "regency_code": f.regency_code,
            "subdistrict_code": f.subdistrict_code, "is_active": f.is_active,
        }
        for f in facs
    ]
    return jsonify(items=items)


@bp.post("")
@require_role(Role.ADMIN)
def create_facility():
    data = request.get_json() or {}
    required = ["name", "code", "facility_type"]
    missing = [k for k in required if k not in data]
    if missing:
        abort(400, description=f"Missing: {', '.join(missing)}")

    fac = HealthcareFacility(
        name=data["name"],
        code=data["code"],
        facility_type=data["facility_type"],
        address=data.get("address"),
        province_code=data.get("province_code"),
        regency_code=data.get("regency_code"),
        subdistrict_code=data.get("subdistrict_code"),
    )
    session().add(fac)
    try:
        session().commit()
    except IntegrityError:
        session().rollback()
        abort(409, description="Facility code already exists")
    return jsonify(
        id=fac.id, name=fac.name, code=fac.code,
        facility_type=fac.facility_type, is_active=fac.is_active,
    ), 201


@bp.put("/<int:fac_id>")
@require_role(Role.ADMIN)
def update_facility(fac_id: int):
    fac = session().get(HealthcareFacility, fac_id)
    if fac is None:
        abort(404, description="Facility not found")
    data = request.get_json() or {}
    for field in ("name", "code", "facility_type", "address",
                  "province_code", "regency_code", "subdistrict_code", "is_active"):
        if field in data:
            setattr(fac, field, data[field])
    session().commit()
    return jsonify(
        id=fac.id, name=fac.name, code=fac.code,
        facility_type=fac.facility_type, is_active=fac.is_active,
    )
