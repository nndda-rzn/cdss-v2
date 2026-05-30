"""Process-wide crypto provider accessor for ORM types.

Set once during create_app(); ORM TypeDecorators read from here.
"""
from app.core.encryption.fernet_provider import FernetProvider
from app.core.encryption.hash_provider import HashProvider

_fernet: FernetProvider | None = None
_hasher: HashProvider | None = None


def set_crypto(fernet: FernetProvider, hasher: HashProvider) -> None:
    global _fernet, _hasher
    _fernet = fernet
    _hasher = hasher


def get_fernet() -> FernetProvider:
    if _fernet is None:
        raise RuntimeError("Crypto not initialized; call set_crypto() in create_app()")
    return _fernet


def get_hasher() -> HashProvider:
    if _hasher is None:
        raise RuntimeError("Crypto not initialized; call set_crypto() in create_app()")
    return _hasher
