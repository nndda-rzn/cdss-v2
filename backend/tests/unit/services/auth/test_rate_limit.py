from app.core.security.rate_limit import LoginRateLimiter


def test_allows_requests_under_limit():
    limiter = LoginRateLimiter(max_attempts=5, window_seconds=60)
    for _ in range(4):
        assert limiter.is_allowed("1.2.3.4") is True


def test_blocks_after_limit_reached():
    limiter = LoginRateLimiter(max_attempts=3, window_seconds=60)
    for _ in range(3):
        limiter.is_allowed("1.2.3.4")
    assert limiter.is_allowed("1.2.3.4") is False


def test_different_ips_independent():
    limiter = LoginRateLimiter(max_attempts=2, window_seconds=60)
    limiter.is_allowed("1.1.1.1")
    limiter.is_allowed("1.1.1.1")
    assert limiter.is_allowed("1.1.1.1") is False
    assert limiter.is_allowed("2.2.2.2") is True


def test_window_expiry_resets():
    from unittest.mock import patch

    limiter = LoginRateLimiter(max_attempts=2, window_seconds=10)
    limiter.is_allowed("1.1.1.1")
    limiter.is_allowed("1.1.1.1")
    assert limiter.is_allowed("1.1.1.1") is False
    # Simulate time passage
    future = limiter._window_start["1.1.1.1"] + 11
    with patch("app.core.security.rate_limit.time.monotonic", return_value=future):
        assert limiter.is_allowed("1.1.1.1") is True
