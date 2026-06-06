"""Global search endpoint: command-palette backing for `Ctrl+K`.

Returns up to 10 patients and 10 encounters matching the query, scoped by the
caller's `facility_id`. Patient name is fully encrypted (Fernet, random IV)
so substring search on name is impossible without decryption; for now we
match on MRN prefix and last-4-of-NIK. Encounters match on chief_complaint
substring (plaintext, not PHI).
"""
from typing import Any

from flask import Blueprint, Response, jsonify, request
from sqlalchemy import ColumnElement, or_, select
from sqlalchemy.orm import Session

from app.api._shared import claims_facility_id, session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.encounter import Encounter
from app.db.models.patient import Patient
from app.services.patient.mask import mask_name

bp = Blueprint("search", __name__, url_prefix="/api/search")

_LIMIT = 10
_MIN_QUERY = 2


def _search_patients(s: Session, *, facility_id: int, q: str) -> list[dict[str, Any]]:
    q_upper = q.upper()
    q_digits = "".join(ch for ch in q if ch.isdigit())
    or_clauses: list[ColumnElement[bool]] = [Patient.mrn.like(f"{q_upper}%")]
    if q_digits and len(q_digits) >= 3:
        or_clauses.append(Patient.nik_last4 == q_digits[-4:])
    rows = s.scalars(
        select(Patient)
        .where(Patient.facility_id == facility_id)
        .where(Patient.deleted_at.is_(None))
        .where(or_(*or_clauses))
        .order_by(Patient.mrn)
        .limit(_LIMIT)
    ).all()
    return [
        {
            "id": str(p.id),
            "mrn": p.mrn,
            "name_masked": mask_name(p.name_encrypted),
            "dob": p.dob.isoformat(),
            "gender": p.gender,
        }
        for p in rows
    ]


def _search_encounters(s: Session, *, facility_id: int, q: str) -> list[dict[str, Any]]:
    rows = s.scalars(
        select(Encounter)
        .where(Encounter.facility_id == facility_id)
        .where(Encounter.chief_complaint.ilike(f"%{q}%"))
        .order_by(Encounter.started_at.desc())
        .limit(_LIMIT)
    ).all()
    return [
        {
            "id": e.id,
            "patient_id": str(e.patient_id),
            "encounter_type": e.encounter_type,
            "status": e.status,
            "chief_complaint": e.chief_complaint,
            "started_at": e.started_at.isoformat(),
        }
        for e in rows
    ]


@bp.get("")
@require_role(Role.ADMIN, Role.CLINICAL, Role.RESEARCHER)
def search() -> Response:
    q = (request.args.get("q") or "").strip()
    if len(q) < _MIN_QUERY:
        return jsonify(patients=[], encounters=[], query=q)

    s = session()
    facility_id = claims_facility_id()
    return jsonify(
        patients=_search_patients(s, facility_id=facility_id, q=q),
        encounters=_search_encounters(s, facility_id=facility_id, q=q),
        query=q,
    )
