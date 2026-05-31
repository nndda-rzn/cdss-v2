"""Patient endpoints: register (more added in later S1/S2 tasks)."""
from typing import cast

from flask import Blueprint, Response, g, jsonify, request
from sqlalchemy.orm import Session

from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.facility import HealthcareFacility
from app.extensions import db
from app.schemas.patient import DuplicateSuggestion, PatientCreate, PatientOut
from app.services.patient.dedup import find_potential_duplicates
from app.services.patient.mask import mask_name
from app.services.patient.register import register_patient

bp = Blueprint("patients", __name__, url_prefix="/api/patients")


def _session() -> Session:
    return cast(Session, db.session)


def _ctx() -> dict[str, str]:
    return {
        "ip_address": request.remote_addr or "unknown",
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "request_id": getattr(g, "request_id", request.headers.get("X-Request-ID", "n/a")),
    }


def _claims_facility_id() -> int:
    from flask_jwt_extended import get_jwt

    return int(get_jwt()["facility_id"])


def _user_id() -> int:
    from flask_jwt_extended import get_jwt_identity

    return int(get_jwt_identity())


@bp.post("")
@require_role(Role.CLINICIAN, Role.NURSE)
def register() -> tuple[Response, int]:
    data = PatientCreate(**(request.get_json() or {}))
    session = _session()
    facility_id = _claims_facility_id()
    facility = session.get(HealthcareFacility, facility_id)
    facility_code = facility.code if facility else "UNK"

    if not request.args.get("confirm_new"):
        dupes = find_potential_duplicates(
            session,
            facility_id=facility_id,
            name=data.name,
            dob=data.dob,
            gender=data.gender,
        )
        if dupes:
            suggestions = [
                DuplicateSuggestion(
                    id=str(p.id),
                    mrn=p.mrn,
                    name_masked=mask_name(p.name_encrypted) or "",
                    dob=p.dob,
                    gender=p.gender,
                ).model_dump(mode="json")
                for p in dupes
            ]
            return (
                jsonify(
                    duplicates=suggestions,
                    action="confirm",
                    message_id="Pasien serupa ditemukan. Pilih atau konfirmasi pasien baru.",
                    message_en="Similar patients found. Pick existing or confirm new.",
                ),
                200,
            )

    patient = register_patient(
        session,
        facility_id=facility_id,
        facility_code=facility_code,
        name=data.name,
        dob=data.dob,
        gender=data.gender,
        nik=data.nik,
        phone=data.phone,
        address=data.address,
        is_pseudonymized=data.is_pseudonymized,
        recorded_by_user_id=_user_id(),
        **_ctx(),
    )
    session.commit()
    return (
        jsonify(
            patient=PatientOut(
                id=str(patient.id),
                mrn=patient.mrn,
                name=patient.name_encrypted,
                dob=patient.dob,
                gender=patient.gender,
                nik_last4=patient.nik_last4,
                phone=patient.phone_encrypted,
                address=patient.address_encrypted,
                facility_id=patient.facility_id,
            ).model_dump(mode="json"),
            action="created",
        ),
        201,
    )
