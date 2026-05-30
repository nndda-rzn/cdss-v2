from pathlib import Path

import pytest

from app.core.encryption.key_loader import load_key


def test_load_key_reads_bytes(tmp_path: Path):
    key_file = tmp_path / "master.key"
    key_file.write_bytes(b"secret-key-bytes")
    assert load_key(str(key_file)) == b"secret-key-bytes"


def test_load_key_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_key(str(tmp_path / "absent.key"))
