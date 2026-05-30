"""Field-level encryption using Fernet (AES-128-CBC + HMAC)."""
from cryptography.fernet import Fernet


class FernetProvider:
    def __init__(self, key: bytes) -> None:
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> bytes:
        return self._fernet.encrypt(plaintext.encode("utf-8"))

    def decrypt(self, token: bytes | None) -> str | None:
        if token is None:
            return None
        return self._fernet.decrypt(token).decode("utf-8")
