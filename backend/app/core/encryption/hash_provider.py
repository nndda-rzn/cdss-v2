"""Irreversible HMAC-SHA256 hashing for identifiers (e.g. NIK)."""
import hashlib
import hmac


class HashProvider:
    def __init__(self, pepper: bytes) -> None:
        self._pepper = pepper

    def hash(self, value: str) -> str:
        return hmac.new(self._pepper, value.encode("utf-8"), hashlib.sha256).hexdigest()
