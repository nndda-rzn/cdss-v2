"""TypeDecorator that stores an HMAC-SHA256 hex digest (irreversible)."""
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from app.db.types.context import get_hasher


class HashedString(TypeDecorator[str]):
    impl = String(64)
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: object) -> str | None:
        if value is None:
            return None
        return get_hasher().hash(value)

    def process_result_value(self, value: str | None, dialect: object) -> str | None:
        return value
