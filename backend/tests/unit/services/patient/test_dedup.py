"""Patient dedup service tests."""
import uuid
from datetime import date, datetime

from app.db.models.patient import Patient
from app.services.patient.dedup import find_potential_duplicates


def _add(session, *, name: str, dob: date, gender: str, mrn: str,
         facility_id: int = 1, deleted: bool = False) -> Patient:
    p = Patient(
        id=uuid.uuid4(),
        facility_id=facility_id,
        mrn=mrn,
        name_encrypted=name,
        dob=dob,
        gender=gender,
        deleted_at=datetime.now() if deleted else None,
    )
    session.add(p)
    session.commit()
    return p


def test_dedup_finds_exact_match(session, seeded_admin):
    _add(session, name="Budi Santoso", dob=date(1965, 3, 12), gender="male",
         mrn="MRN-P1-000001")
    matches = find_potential_duplicates(
        session, facility_id=1, name="Budi Santoso",
        dob=date(1965, 3, 12), gender="male",
    )
    assert len(matches) == 1
    assert matches[0].mrn == "MRN-P1-000001"


def test_dedup_fuzzy_match_typo(session, seeded_admin):
    _add(session, name="Budi Santoso", dob=date(1965, 3, 12), gender="male",
         mrn="MRN-P1-000001")
    # One-char typo should still match (Levenshtein <= 2)
    matches = find_potential_duplicates(
        session, facility_id=1, name="Budi Santosa",
        dob=date(1965, 3, 12), gender="male",
    )
    assert len(matches) == 1


def test_dedup_no_match_different_name(session, seeded_admin):
    _add(session, name="Budi Santoso", dob=date(1965, 3, 12), gender="male",
         mrn="MRN-P1-000001")
    matches = find_potential_duplicates(
        session, facility_id=1, name="Siti Aminah",
        dob=date(1965, 3, 12), gender="male",
    )
    assert matches == []


def test_dedup_excludes_different_dob(session, seeded_admin):
    _add(session, name="Budi Santoso", dob=date(1965, 3, 12), gender="male",
         mrn="MRN-P1-000001")
    matches = find_potential_duplicates(
        session, facility_id=1, name="Budi Santoso",
        dob=date(1970, 1, 1), gender="male",
    )
    assert matches == []


def test_dedup_excludes_deleted(session, seeded_admin):
    _add(session, name="Budi Santoso", dob=date(1965, 3, 12), gender="male",
         mrn="MRN-P1-000001", deleted=True)
    matches = find_potential_duplicates(
        session, facility_id=1, name="Budi Santoso",
        dob=date(1965, 3, 12), gender="male",
    )
    assert matches == []
