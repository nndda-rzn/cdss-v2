"""Patient T1 masking helper tests."""
from app.services.patient.mask import mask_name, mask_nik, mask_phone


def test_mask_name_multiword():
    assert mask_name("Budi Santoso") == "B*** S******"


def test_mask_name_single_char_word():
    assert mask_name("A") == "A"


def test_mask_name_none():
    assert mask_name(None) is None


def test_mask_nik_full():
    assert mask_nik("3201123456780001") == "************0001"


def test_mask_nik_none():
    assert mask_nik(None) is None


def test_mask_phone_last4_visible():
    assert mask_phone("0812345678") == "******5678"


def test_mask_phone_short():
    # 4 or fewer chars: fully masked
    assert mask_phone("123") == "***"


def test_mask_phone_none():
    assert mask_phone(None) is None
