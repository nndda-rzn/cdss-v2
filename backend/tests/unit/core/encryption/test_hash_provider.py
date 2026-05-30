from app.core.encryption.hash_provider import HashProvider


def test_hmac_is_deterministic():
    provider = HashProvider(b"pepper-bytes")
    h1 = provider.hash("3171234567890001")
    h2 = provider.hash("3171234567890001")
    assert h1 == h2
    assert len(h1) == 64


def test_hmac_differs_per_input():
    provider = HashProvider(b"pepper-bytes")
    assert provider.hash("111") != provider.hash("222")


def test_different_pepper_differs():
    a = HashProvider(b"pepper-a").hash("111")
    b = HashProvider(b"pepper-b").hash("111")
    assert a != b
