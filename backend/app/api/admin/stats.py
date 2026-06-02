"""Admin dashboard stats endpoint."""
from __future__ import annotations

from datetime import UTC, datetime, time, timedelta

from flask import Blueprint, jsonify
from sqlalchemy import func, select

from app.api._shared import session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.ai_analysis import AIAnalysis
from app.db.models.audit_log import AuditLog
from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.facility import HealthcareFacility
from app.db.models.model_metadata import ModelMetadata
from app.db.models.patient import Patient
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User

bp = Blueprint("admin_stats", __name__, url_prefix="/stats")


def _start_of_today_utc() -> datetime:
    return datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)


@bp.get("")
@require_role(Role.ADMIN)
def get_stats():
    s = session()
    today = _start_of_today_utc()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)

    # Users
    total_users = s.scalar(select(func.count(User.id))) or 0
    active_users = s.scalar(
        select(func.count(User.id)).where(User.is_active.is_(True))
    ) or 0
    by_role = {}
    for role_name, count in s.execute(
        select(User.role, func.count(User.id)).group_by(User.role)
    ).all():
        by_role[role_name] = count

    # Facilities
    total_facilities = s.scalar(select(func.count(HealthcareFacility.id))) or 0

    # Active sessions
    active_sessions = s.scalar(
        select(func.count(RefreshToken.id))
        .where(RefreshToken.revoked_at.is_(None))
        .where(RefreshToken.expires_at > datetime.now(UTC))
    ) or 0

    # Active model
    active_model = s.scalar(
        select(ModelMetadata).where(ModelMetadata.is_active.is_(True)).limit(1)
    )

    # Patients
    total_patients = s.scalar(select(func.count(Patient.id))) or 0

    # Encounters
    encounters_today = s.scalar(
        select(func.count(Encounter.id)).where(Encounter.started_at >= today)
    ) or 0
    encounters_yesterday = s.scalar(
        select(func.count(Encounter.id))
        .where(Encounter.started_at >= yesterday)
        .where(Encounter.started_at < today)
    ) or 0

    # ECG Studies
    ecg_today = s.scalar(
        select(func.count(ECGStudy.id)).where(ECGStudy.acquired_at >= today)
    ) or 0
    ecg_yesterday = s.scalar(
        select(func.count(ECGStudy.id))
        .where(ECGStudy.acquired_at >= yesterday)
        .where(ECGStudy.acquired_at < today)
    ) or 0

    # AI Performance
    ai_today = s.scalar(
        select(func.count(AIAnalysis.id)).where(AIAnalysis.created_at >= today)
    ) or 0
    ai_yesterday = s.scalar(
        select(func.count(AIAnalysis.id))
        .where(AIAnalysis.created_at >= yesterday)
        .where(AIAnalysis.created_at < today)
    ) or 0

    avg_inference = s.scalar(
        select(func.avg(AIAnalysis.inference_time_ms))
        .where(AIAnalysis.created_at >= week_ago)
    ) or 0

    avg_confidence = s.scalar(
        select(func.avg(AIAnalysis.confidence_score))
        .where(AIAnalysis.created_at >= week_ago)
    ) or 0

    # AI trend (7 days)
    inference_trend = []
    confidence_trend = []
    for i in range(7):
        day = today - timedelta(days=6 - i)
        next_day = day + timedelta(days=1)
        day_avg_ms = s.scalar(
            select(func.avg(AIAnalysis.inference_time_ms))
            .where(AIAnalysis.created_at >= day)
            .where(AIAnalysis.created_at < next_day)
        )
        day_avg_conf = s.scalar(
            select(func.avg(AIAnalysis.confidence_score))
            .where(AIAnalysis.created_at >= day)
            .where(AIAnalysis.created_at < next_day)
        )
        inference_trend.append({
            "date": day.strftime("%Y-%m-%d"),
            "avg_ms": round(float(day_avg_ms), 1) if day_avg_ms else None,
        })
        confidence_trend.append({
            "date": day.strftime("%Y-%m-%d"),
            "avg": round(float(day_avg_conf), 3) if day_avg_conf else None,
        })

    # Recent audit (last 10)
    audit_rows = s.scalars(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(10)
    ).all()
    audit = [
        {
            "user_id": a.user_id,
            "action": a.action,
            "entity_type": a.entity_type,
            "entity_id": a.entity_id,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in audit_rows
    ]

    return jsonify(
        users={"total": total_users, "active": active_users, "by_role": by_role},
        facilities={"total": total_facilities},
        sessions={"active": active_sessions},
        model={
            "name": active_model.model_name if active_model else None,
            "version": active_model.model_version if active_model else None,
            "is_active": active_model is not None,
        },
        patients={"total": total_patients},
        encounters={"today": encounters_today, "yesterday": encounters_yesterday},
        ecg={"today": ecg_today, "yesterday": ecg_yesterday},
        ai={
            "analyses_today": ai_today,
            "yesterday": ai_yesterday,
            "avg_inference_ms": round(float(avg_inference), 1),
            "avg_confidence": round(float(avg_confidence), 3),
            "inference_trend": inference_trend,
            "confidence_trend": confidence_trend,
        },
        audit=audit,
    )
