"""Patient search service tests."""
import uuid
from datetime import date, datetime

from app.db.models.patient import Patient
from app.services.patient.search import search_patients


def _add(session, *, name, dob, gender, mrn, nik_last4=None, phone=None,
         facility_id=1, deleted=False):
    p = Patient(
        id=uuid.uuid4(),
        facility_id=facility_id,
        mrn=mrn,
        name_encrypted=name,
        dob=dob,
        gender=gender,
        nik_last4=nik_last4,
        phone_encrypted=phone,
        deleted_at=datetime.now() if deleted else None,
    )
    session.add(p)
    session.commit()
    return p


def test_search_returns_masked_results(session, seeded_admin):
    _add(session, name="Budi Santoso", dob=date(1965, 3, 12), gender="male",
         mrn="MRN-P1-000001", nik_last4="0001", phone="0812345678")
    result = search_patients(session, facility_id=1)
    assert result["total"] == 1
    item = result["items"][0]
    assert item["name_masked"] == "B*** S******"
    assert item["phone_masked"] == "******5678"
    assert item["nik_last4"] == "0001"
    assert "name" not in item


def test_search_by_mrn(session, seeded_admin):
    _add(session, name="Budi", dob=date(1965, 3, 12), gender="male",
         mrn="MRN-P1-000001")
    _add(session, name="Siti", dob=date(1980, 1, 1), gender="female",
         mrn="MRN-P1-000002")
    result = search_patients(session, facility_id=1, mrn="MRN-P1-000002")
    assert result["total"] == 1
    assert result["items"][0]["mrn"] == "MRN-P1-000002"


def test_search_by_nik_last4(session, seeded_admin):
    _add(session, name="Budi", dob=date(1965, 3, 12), gender="male",
         mrn="MRN-P1-000001", nik_last4="0001")
    _add(session, name="Siti", dob=date(1980, 1, 1), gender="female",
         mrn="MRN-P1-000002", nik_last4="9999")
    result = search_patients(session, facility_id=1, nik_last4="9999")
    assert result["total"] == 1
    assert result["items"][0]["mrn"] == "MRN-P1-000002"


def test_search_excludes_deleted(session, seeded_admin):
    _add(session, name="Budi", dob=date(1965, 3, 12), gender="male",
         mrn="MRN-P1-000001", deleted=True)
    result = search_patients(session, facility_id=1)
    assert result["total"] == 0


def test_search_pagination(session, seeded_admin):
    for i in range(1, 6):
        _add(session, name=f"P{i}", dob=date(1990, 1, 1), gender="male",
             mrn=f"MRN-P1-00000{i}")
    result = search_patients(session, facility_id=1, page=1, page_size=2)
    assert result["total"] == 5
    assert len(result["items"]) == 2
    assert result["page"] == 1
    assert result["page_size"] == 2
