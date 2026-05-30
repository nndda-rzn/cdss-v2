import json

import structlog

from app.core.logging.config import configure_logging


def test_logging_emits_json(capsys):
    configure_logging()
    log = structlog.get_logger()
    log.info("login_ok", user_id=1, request_id="req-1")
    out = capsys.readouterr().out
    record = json.loads(out.strip().splitlines()[-1])
    assert record["event"] == "login_ok"
    assert record["user_id"] == 1
    assert record["request_id"] == "req-1"
    assert "timestamp" in record
