import pytest
from cryptography.fernet import Fernet

from app.core.encryption.fernet_provider import FernetProvider
from app.core.encryption.hash_provider import HashProvider
from app.db.types.context import get_fernet, get_hasher, set_crypto


def test_set_and_get_crypto():
    set_crypto(FernetProvider(Fernet.generate_key()), HashProvider(b"pepper"))
    assert get_fernet() is not None
    assert get_hasher() is not None


def test_get_without_set_raises(monkeypatch):
    import app.db.types.context as ctx
    monkeypatch.setattr(ctx, "_fernet", None)
    with pytest.raises(RuntimeError):
        get_fernet()
