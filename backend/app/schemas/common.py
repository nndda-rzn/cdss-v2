"""Shared schema primitives."""
from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message_id: str
    message_en: str
    field: str | None = None
    request_id: str | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorBody
