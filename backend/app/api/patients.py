"""Patient endpoints: register, list, detail, update, soft-delete."""
import uuid

from flask import Blueprint, Response, jsonify, request

from app.api._shared import (
    claims_facility_id,
    current_role,
    current_user_id,
    request_ctx,
    session,
)
from app.core.exceptions.base import NotFoundError
from app.core.rbac.decorators import require_role
from app.core.rbac.patient_policy import filter_patient_detail_for_role
from app.core.rbac.roles import Role
from app.db.models.facility import HealthcareFacility
from app.db.models.patient import Patient
from app.schemas.patient import DuplicateSuggestion, PatientCreate, PatientOut
from app.services.patient.dedup import find_potential_duplicates
from app.services.patient.delete import soft_delete_patient
from app.services.patient.mask import mask_name
from app.services.patient.register import register_patient
from app.services.patient.reveal import get_patient_detail
from app.services.patient.search import search_patients

bp = Blueprint("patients", __name__, url_prefix="/api/patients")

_READ_ROLES = (
    Role.ADMIN,
    Role.CLINICIAN,
    Role.NURSE,
    Role.EXPERT_REVIEWER,
    Role.RESEARCHER,
)


@bp.post("")
@require_role(Role.CLINICIAN, Role.NURSE)
def register() -> tuple[Response, int]:
    data = PatientCreate(**(request.get_json() or {}))
    s = session()
    facility_id = claims_facility_id()
    facility = s.get(HealthcareFacility, facility_id)
    facility_code = facility.code if facility else "UNK"

    if not request.args.get("confirm_new"):
        dupes = find_potential_duplicates(
            s,
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
        s,
        facility_id=facility_id,
        facility_code=facility_code,
        name=data.name,
        dob=data.dob,
        gender=data.gender,
        nik=data.nik,
        phone=data.phone,
        address=data.address,
        is_pseudonymized=data.is_pseudonymized,
        recorded_by_user_id=current_user_id(),
        **request_ctx(),
    )
    s.commit()
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


@bp.get("")
@require_role(*_READ_ROLES)
def list_patients() -> Response:
    s = session()
    args = request.args
    include_deleted = args.get("include_deleted") == "true" and current_role() == "admin"
    result = search_patients(
        s,
        facility_id=claims_facility_id(),
        mrn=args.get("mrn"),
        nik_last4=args.get("nik_last4"),
        gender=args.get("gender"),
        include_deleted=include_deleted,
        page=int(args.get("page", 1)),
        page_size=int(args.get("page_size", 20)),
    )
    return jsonify(**result)


@bp.get("/<patient_id>")
@require_role(*_READ_ROLES)
def get_patient(patient_id: str) -> Response:
    s = session()
    pid = uuid.UUID(patient_id)
    role = current_role()

    # Research roles never decrypt T1: shape from a non-revealing read so no
    # PHIAccessLog is written and no identifier leaves the service.
    if role in ("researcher", "expert_reviewer"):
        patient = s.get(Patient, pid)
        if patient is None or patient.deleted_at is not None:
            raise NotFoundError(
                code="PATIENT_NOT_FOUND",
                message_id="Pasien tidak ditemukan",
                message_en="Patient not found",
            )
        return jsonify(
            filter_patient_detail_for_role(
                {
                    "id": str(patient.id),
                    "dob": patient.dob.isoformat(),
                    "gender": patient.gender,
                    "facility_id": patient.facility_id,
                },
                role,
            )
        )

    detail = get_patient_detail(
        s,
        patient_id=pid,
        user_id=current_user_id(),
        ip_address=request.remote_addr,
    )
    s.commit()
    return jsonify(**detail)


@bp.patch("/<patient_id>")
@require_role(Role.CLINICIAN, Role.NURSE)
def update_patient(patient_id: str) -> Response:
    s = session()
    patient = s.get(Patient, uuid.UUID(patient_id))
    if patient is None or patient.deleted_at is not None:
        raise NotFoundError(
            code="PATIENT_NOT_FOUND",
            message_id="Pasien tidak ditemukan",
            message_en="Patient not found",
        )
    data = request.get_json() or {}
    for field, column in (
        ("name", "name_encrypted"),
        ("phone", "phone_encrypted"),
        ("address", "address_encrypted"),
    ):
        if field in data:
            setattr(patient, column, data[field])
    s.commit()
    return jsonify(status="ok")


@bp.delete("/<patient_id>")
@require_role(Role.ADMIN)
def delete_patient(patient_id: str) -> Response:
    s = session()
    body = request.get_json() or {}
    soft_delete_patient(
        s,
        patient_id=uuid.UUID(patient_id),
        user_id=current_user_id(),
        reason=body.get("reason", ""),
        **request_ctx(),
    )
    s.commit()
    return jsonify(status="ok")