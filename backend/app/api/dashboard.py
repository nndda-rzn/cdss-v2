"""Dashboard endpoints: aggregate counters and recent activity for the home page.

Scoped by the caller's `facility_id` claim so multi-facility deployments stay
isolated, consistent with the rest of the API surface.
"""
from datetime import UTC, datetime, time, timedelta

from flask import Blueprint, Response, jsonify
from sqlalchemy import func, select

from app.api._shared import claims_facility_id, session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.ai_analysis import AIAnalysis
from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.patient import Patient

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

_RECENT_LIMIT = 5


def _start_of_today_utc() -> datetime:
    return datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)


@bp.get("/stats")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.RESEARCHER)
def get_stats() -> Response:
    s = session()
    facility_id = claims_facility_id()

    total_patients = s.scalar(
        select(func.count(Patient.id))
        .where(Patient.facility_id == facility_id)
        .where(Patient.deleted_at.is_(None))
    ) or 0

    active_encounters = s.scalar(
        select(func.count(Encounter.id))
        .where(Encounter.facility_id == facility_id)
        .where(Encounter.status == "open")
    ) or 0

    today = _start_of_today_utc()
    analyses_today = s.scalar(
        select(func.count(AIAnalysis.id))
        .join(ECGStudy, ECGStudy.id == AIAnalysis.ecg_study_id)
        .join(Encounter, Encounter.id == ECGStudy.encounter_id)
        .where(Encounter.facility_id == facility_id)
        .where(AIAnalysis.created_at >= today)
    ) or 0

    pending_tasks = active_encounters

    recent_rows = s.scalars(
        select(Encounter)
        .where(Encounter.facility_id == facility_id)
        .order_by(Encounter.started_at.desc())
        .limit(_RECENT_LIMIT)
    ).all()
    recent = [
        {
            "id": e.id,
            "patient_id": str(e.patient_id),
            "encounter_type": e.encounter_type,
            "status": e.status,
            "chief_complaint": e.chief_complaint,
            "started_at": e.started_at.isoformat(),
        }
        for e in recent_rows
    ]

    # Encounter trend (7 days)
    encounter_trend = []
    for i in range(7):
        day = today - timedelta(days=6 - i)
        next_day = day + timedelta(days=1)
        count = s.scalar(
            select(func.count(Encounter.id))
            .where(Encounter.facility_id == facility_id)
            .where(Encounter.started_at >= day)
            .where(Encounter.started_at < next_day)
        ) or 0
        encounter_trend.append({"date": day.strftime("%Y-%m-%d"), "count": count})

    # Diagnosis distribution
    diagnosis_rows = s.execute(
        select(AIAnalysis.predicted_class, func.count(AIAnalysis.id))
        .join(ECGStudy, ECGStudy.id == AIAnalysis.ecg_study_id)
        .join(Encounter, Encounter.id == ECGStudy.encounter_id)
        .where(Encounter.facility_id == facility_id)
        .group_by(AIAnalysis.predicted_class)
    ).all()
    diagnosis_distribution = {row[0]: row[1] for row in diagnosis_rows}

    # ECG quality distribution
    quality_rows = s.execute(
        select(ECGStudy.image_quality_status, func.count(ECGStudy.id))
        .join(Encounter, Encounter.id == ECGStudy.encounter_id)
        .where(Encounter.facility_id == facility_id)
        .group_by(ECGStudy.image_quality_status)
    ).all()
    ecg_quality_distribution = {row[0]: row[1] for row in quality_rows}

    return jsonify(
        total_patients=total_patients,
        active_encounters=active_encounters,
        analyses_today=analyses_today,
        pending_tasks=pending_tasks,
        recent_encounters=recent,
        encounter_trend=encounter_trend,
        diagnosis_distribution=diagnosis_distribution,
        ecg_quality_distribution=ecg_quality_distribution,
    )
