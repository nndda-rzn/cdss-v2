"""bcrypt password hashing (direct bcrypt library).

bcrypt has a 72-byte input limit; bcrypt 5.x raises on longer input, so we
truncate to 72 bytes (classic bcrypt behavior) for stability.
"""
import bcrypt

_DEFAULT_ROUNDS = 12
_MAX_BYTES = 72


def _to_bytes(plain: str) -> bytes:
    return plain.encode("utf-8")[:_MAX_BYTES]


def hash_password(plain: str, rounds: int = _DEFAULT_ROUNDS) -> str:
    hashed = bcrypt.hashpw(_to_bytes(plain), bcrypt.gensalt(rounds))
    return hashed.decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_to_bytes(plain), hashed.encode("ascii"))
