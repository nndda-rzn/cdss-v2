"""Validate an uploaded image by size and magic bytes (not the client MIME)."""
from app.core.exceptions.base import ValidationError

_MAX_BYTES = 10 * 1024 * 1024
_MIN_BYTES = 1024

_MAGIC = {
    "jpeg": (b"\xff\xd8\xff",),
    "png": (b"\x89PNG\r\n\x1a\n",),
}
_EXT = {"jpeg": "jpg", "png": "png"}


def validate_image(data: bytes, *, content_type: str | None = None) -> tuple[str, str]:
    """Return (format, ext) for a valid JPEG/PNG; raise ValidationError otherwise.

    The client-supplied content_type is advisory only; the format is decided by
    magic bytes to prevent spoofing.
    """
    size = len(data)
    if size < _MIN_BYTES:
        raise ValidationError(
            code="FILE_TOO_SMALL",
            message_id="Berkas terlalu kecil",
            message_en="File is too small",
        )
    if size > _MAX_BYTES:
        raise ValidationError(
            code="FILE_TOO_LARGE",
            message_id="Berkas melebihi 10 MB",
            message_en="File exceeds 10 MB",
        )
    for fmt, signatures in _MAGIC.items():
        if any(data.startswith(sig) for sig in signatures):
            return fmt, _EXT[fmt]
    raise ValidationError(
        code="INVALID_FILE_FORMAT",
        message_id="Format berkas harus JPEG atau PNG",
        message_en="File format must be JPEG or PNG",
    )
