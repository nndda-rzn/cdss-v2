"""Generate Fernet master key + HMAC pepper. Idempotent; never overwrites."""
import os
import sys
from pathlib import Path

from cryptography.fernet import Fernet


def generate_secrets(key_path: str, pepper_path: str) -> None:
    kp = Path(key_path)
    pp = Path(pepper_path)
    kp.parent.mkdir(parents=True, exist_ok=True)
    if not kp.exists():
        kp.write_bytes(Fernet.generate_key())
        os.chmod(kp, 0o600)
    if not pp.exists():
        pp.write_bytes(os.urandom(32))
        os.chmod(pp, 0o600)


if __name__ == "__main__":
    key = os.environ.get("MASTER_KEY_PATH", "secrets/master.key")
    pepper = os.environ.get("HMAC_PEPPER_PATH", "secrets/hmac_pepper.key")
    generate_secrets(key, pepper)
    print(f"Secrets ready: {key}, {pepper}", file=sys.stderr)
