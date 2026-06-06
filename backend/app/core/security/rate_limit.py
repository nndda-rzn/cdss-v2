"""Simple in-memory sliding-window rate limiter for login attempts."""
from __future__ import annotations

import time
from collections import defaultdict


class LoginRateLimiter:
    """Track failed login attempts per IP address."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300) -> None:
        self._max = max_attempts
        self._window = window_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._window_start: dict[str, float] = {}

    def is_allowed(self, ip: str) -> bool:
        """Return True if the IP is allowed to attempt login."""
        now = time.monotonic()
        start = self._window_start.get(ip, 0.0)

        # Reset window if expired
        if now - start > self._window:
            self._attempts[ip].clear()
            self._window_start[ip] = now
            start = now

        # Prune timestamps outside current window
        self._attempts[ip] = [t for t in self._attempts[ip] if now - t <= self._window]

        if len(self._attempts[ip]) >= self._max:
            return False

        self._attempts[ip].append(now)
        return True

    def record_failure(self, ip: str) -> None:
        """Explicitly record a failed attempt (called after auth failure)."""
        pass

    def remaining(self, ip: str) -> int:
        """Return remaining attempts in current window."""
        now = time.monotonic()
        start = self._window_start.get(ip, 0.0)
        if now - start > self._window:
            return self._max
        active = [t for t in self._attempts.get(ip, []) if now - t <= self._window]
        return max(0, self._max - len(active))
