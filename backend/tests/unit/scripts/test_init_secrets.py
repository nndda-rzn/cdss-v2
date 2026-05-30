import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.init_secrets import generate_secrets


def test_generates_key_and_pepper(tmp_path: Path):
    key_path = tmp_path / "master.key"
    pepper_path = tmp_path / "hmac_pepper.key"
    generate_secrets(str(key_path), str(pepper_path))
    assert key_path.exists()
    assert pepper_path.exists()
    assert len(key_path.read_bytes()) > 0


def test_does_not_overwrite(tmp_path: Path):
    key_path = tmp_path / "master.key"
    pepper_path = tmp_path / "hmac_pepper.key"
    key_path.write_bytes(b"existing")
    generate_secrets(str(key_path), str(pepper_path))
    assert key_path.read_bytes() == b"existing"
