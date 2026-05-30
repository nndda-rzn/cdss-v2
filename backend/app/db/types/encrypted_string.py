"""TypeDecorator that encrypts str -> bytes (Fernet) at rest."""
from sqlalchemy import LargeBinary
from sqlalchemy.types import TypeDecorator

from app.db.types.context import get_fernet


class EncryptedString(TypeDecorator[str]):
    impl = LargeBinary
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: object) -> bytes | None:
        if value is None:
            return None
        return get_fernet().encrypt(value)

    def process_result_value(self, value: bytes | None, dialect: object) -> str | None:
        if value is None:
            return None
        return get_fernet().decrypt(value)
