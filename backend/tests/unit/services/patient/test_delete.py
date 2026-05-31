"""Patient soft-delete service tests."""
import uuid
from datetime import date

import pytest
from sqlalchemy import select

from app.core.exceptions.base import NotFoundError, ValidationError
from app.db.models.audit_log import AuditLog
from app.db.models.patient import Patient
from app.services.patient.delete import soft_delete_patient


def _add(session, *, mrn="MRN-P1-000001", facility_id=1) -> Patient:
    p = Patient(
        id=uuid.uuid4(),
        facility_id=facility_id,
        mrn=mrn,
        name_encrypted="Budi",
        dob=date(1965, 3, 12),
        gender="male",
    )
    session.add(p)
    session.commit()
    return p


def test_soft_delete_sets_deleted_at(session, seeded_admin):
    p = _add(session)
    soft_delete_patient(
        session, patient_id=p.id, user_id=1, reason="duplikat data"
    )
    session.commit()
    refreshed = session.get(Patient, p.id)
    assert refreshed is not None
    assert refreshed.deleted_at is not None


def test_soft_delete_requires_reason(session, seeded_admin):
    p = _add(session)
    with pytest.raises(ValidationError) as exc:
        soft_delete_patient(session, patient_id=p.id, user_id=1, reason="")
    assert exc.value.code == "PATIENT_DELETE_REASON_REQUIRED"


def test_soft_delete_already_deleted_raises(session, seeded_admin):
    p = _add(session)
    soft_delete_patient(session, patient_id=p.id, user_id=1, reason="x")
    session.commit()
    with pytest.raises(NotFoundError):
        soft_delete_patient(session, patient_id=p.id, user_id=1, reason="x")


def test_soft_delete_unknown_raises(session, seeded_admin):
    with pytest.raises(NotFoundError):
        soft_delete_patient(
            session, patient_id=uuid.uuid4(), user_id=1, reason="x"
        )


def test_soft_delete_writes_audit_with_reason(session, seeded_admin):
    p = _add(session)
    soft_delete_patient(
        session, patient_id=p.id, user_id=1, reason="permintaan pasien"
    )
    session.commit()
    row = session.scalar(
        select(AuditLog).where(AuditLog.action == "patient_soft_delete")
    )
    assert row is not None
    assert "permintaan pasien" in (row.description or "")
