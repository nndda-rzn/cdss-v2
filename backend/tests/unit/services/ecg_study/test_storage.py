"""ECG storage helper tests."""
from app.services.ecg_study.storage import (
    generate_study_uid,
    save_image,
    storage_path_for,
)


def test_generate_study_uid_format():
    uid = generate_study_uid("P1")
    assert uid.startswith("ECG-P1-")
    parts = uid.split("-")
    assert len(parts) == 4  # ECG, P1, timestamp, random4
    assert len(parts[3]) == 4


def test_storage_path_for_relative():
    rel = storage_path_for(facility_id=1, encounter_id=2,
                           study_uid="ECG-P1-x-abcd", ext="jpg")
    assert rel == "uploads/ecg/1/2/ECG-P1-x-abcd.jpg"


def test_save_image_writes_file(tmp_path):
    rel = "uploads/ecg/1/2/ECG-P1-x-abcd.jpg"
    save_image(tmp_path, rel, b"\xff\xd8imagebytes")
    written = tmp_path / rel
    assert written.exists()
    assert written.read_bytes() == b"\xff\xd8imagebytes"
