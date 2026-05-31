"""Application exception hierarchy mapping to the bilingual error envelope."""

class AppException(Exception):  # noqa: N818
    http_status = 500

    def __init__(self, code: str, message_id: str, message_en: str,
                 field: str | None = None) -> None:
        super().__init__(message_en)
        self.code = code
        self.message_id = message_id
        self.message_en = message_en
        self.field = field

class AuthError(AppException):
    http_status = 401

class ValidationError(AppException):
    http_status = 422

class NotFoundError(AppException):
    http_status = 404

class ConflictError(AppException):
    http_status = 409

class ForbiddenError(AppException):
    http_status = 403
