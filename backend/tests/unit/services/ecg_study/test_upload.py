"""ECG upload validation tests."""
import pytest

from app.core.exceptions.base import ValidationError
from app.services.ecg_study.upload import validate_image

# Minimal valid magic-byte headers padded to clear the 1KB minimum.
_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 2048
_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 2048
_GIF = b"GIF89a" + b"\x00" * 2048


def test_validate_jpeg_ok():
    fmt, ext = validate_image(_JPEG, content_type="image/jpeg")
    assert fmt == "jpeg"
    assert ext == "jpg"


def test_validate_png_ok():
    fmt, ext = validate_image(_PNG, content_type="image/png")
    assert fmt == "png"
    assert ext == "png"


def test_validate_rejects_gif():
    with pytest.raises(ValidationError) as exc:
        validate_image(_GIF, content_type="image/gif")
    assert exc.value.code == "INVALID_FILE_FORMAT"


def test_validate_rejects_too_large():
    big = _JPEG + b"\x00" * (10 * 1024 * 1024 + 1)
    with pytest.raises(ValidationError) as exc:
        validate_image(big, content_type="image/jpeg")
    assert exc.value.code == "FILE_TOO_LARGE"


def test_validate_rejects_too_small():
    with pytest.raises(ValidationError) as exc:
        validate_image(b"\xff\xd8", content_type="image/jpeg")
    assert exc.value.code == "FILE_TOO_SMALL"
