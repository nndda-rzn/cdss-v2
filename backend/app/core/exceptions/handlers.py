"""Global Flask error handlers -> bilingual JSON envelope."""
from flask import Flask, Response, g, jsonify, request

from app.core.exceptions.base import AppException


def _request_id() -> str:
    return getattr(g, "request_id", None) or request.headers.get("X-Request-ID", "n/a")


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppException)
    def _handle_app_exception(err: AppException) -> tuple[Response, int]:
        payload = {
            "error": {
                "code": err.code,
                "message_id": err.message_id,
                "message_en": err.message_en,
                "field": err.field,
                "request_id": _request_id(),
            }
        }
        return jsonify(payload), err.http_status

    @app.errorhandler(500)
    def _handle_500(_err: object) -> tuple[Response, int]:
        payload = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message_id": "Terjadi kesalahan sistem",
                "message_en": "Internal server error",
                "field": None,
                "request_id": _request_id(),
            }
        }
        return jsonify(payload), 500
