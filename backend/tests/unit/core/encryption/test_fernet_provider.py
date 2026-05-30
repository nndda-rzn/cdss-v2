from cryptography.fernet import Fernet

from app.core.encryption.fernet_provider import FernetProvider


def test_roundtrip_encrypt_decrypt():
    key = Fernet.generate_key()
    provider = FernetProvider(key)
    token = provider.encrypt("Budi Santoso")
    assert token != b"Budi Santoso"
    assert provider.decrypt(token) == "Budi Santoso"


def test_decrypt_none_returns_none():
    provider = FernetProvider(Fernet.generate_key())
    assert provider.decrypt(None) is None
