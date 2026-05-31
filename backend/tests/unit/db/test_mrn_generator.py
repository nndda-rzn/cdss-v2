"""MRN generator tests."""
import uuid
from datetime import date

import pytest

from app.db.models.patient import Patient
from app.db.mrn_generator import MRN_GENERATION_EXHAUSTED, generate_mrn


def _add_patient(session, *, facility_id: int, mrn: str) -> None:
    session.add(
        Patient(
            id=uuid.uuid4(),
            facility_id=facility_id,
            mrn=mrn,
            name_encrypted="X",
            dob=date(1990, 1, 1),
            gender="male",
        )
    )
    session.commit()


def test_mrn_format_zero_padded(session, seeded_admin):
    mrn = generate_mrn(session, facility_id=1, facility_code="P1")
    assert mrn == "MRN-P1-000001"


def test_mrn_increments_after_insert(session, seeded_admin):
    first = generate_mrn(session, facility_id=1, facility_code="P1")
    _add_patient(session, facility_id=1, mrn=first)
    second = generate_mrn(session, facility_id=1, facility_code="P1")
    assert second == "MRN-P1-000002"


def test_mrn_per_facility_isolation(session, seeded_admin):
    from app.db.models.facility import HealthcareFacility

    session.add(
        HealthcareFacility(id=2, name="P2", code="P2", facility_type="pustu")
    )
    session.commit()

    mrn1 = generate_mrn(session, facility_id=1, facility_code="P1")
    _add_patient(session, facility_id=1, mrn=mrn1)
    mrn2 = generate_mrn(session, facility_id=2, facility_code="P2")
    assert mrn1 == "MRN-P1-000001"
    assert mrn2 == "MRN-P2-000001"


def test_mrn_exhaustion_raises(session, seeded_admin):
    _add_patient(session, facility_id=1, mrn="MRN-P1-999999")
    with pytest.raises(RuntimeError) as exc:
        generate_mrn(session, facility_id=1, facility_code="P1")
    assert MRN_GENERATION_EXHAUSTED in str(exc.value)
