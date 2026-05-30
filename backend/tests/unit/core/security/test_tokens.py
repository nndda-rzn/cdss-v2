from app.core.security.tokens import generate_refresh_token, hash_token


def test_generate_is_unique_and_hashable():
    raw1, _ = generate_refresh_token()
    raw2, _ = generate_refresh_token()
    assert raw1 != raw2
    assert len(raw1) >= 32


def test_hash_is_deterministic():
    raw, h = generate_refresh_token()
    assert h == hash_token(raw)
    assert len(h) == 64
