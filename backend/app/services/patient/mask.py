"""Pure masking helpers for T1 identifiers (display in lists, no decryption log).

Each helper keeps a small visible hint (first letter of each name word, last 4
digits of NIK/phone) and masks the rest with '*'. None passes through.
"""


def mask_name(value: str | None) -> str | None:
    if value is None:
        return None
    parts = value.split(" ")
    masked = [p[0] + "*" * (len(p) - 1) if len(p) > 1 else p for p in parts]
    return " ".join(masked)


def mask_nik(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) <= 4:
        return "*" * len(value)
    return "*" * (len(value) - 4) + value[-4:]


def mask_phone(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) <= 4:
        return "*" * len(value)
    return "*" * (len(value) - 4) + value[-4:]
