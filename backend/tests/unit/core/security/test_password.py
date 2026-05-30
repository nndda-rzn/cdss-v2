from app.core.security.password import hash_password, verify_password


def test_hash_and_verify():
    h = hash_password("s3cret", rounds=4)
    assert h != "s3cret"
    assert verify_password("s3cret", h) is True
    assert verify_password("wrong", h) is False


def test_long_password_truncated_not_error():
    # >72 bytes must not raise (classic bcrypt truncation behavior)
    long_pw = "a" * 100
    h = hash_password(long_pw, rounds=4)
    assert verify_password(long_pw, h) is True
    # first 72 bytes identical => same verification (bcrypt truncates)
    assert verify_password("a" * 72, h) is True
