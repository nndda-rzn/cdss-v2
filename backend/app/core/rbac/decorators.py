"""@require_role decorator built on Flask-JWT-Extended."""
from collections.abc import Callable
from functools import wraps
from typing import Any

from flask_jwt_extended import get_jwt, verify_jwt_in_request

from app.core.exceptions.base import ForbiddenError
from app.core.rbac.roles import Role


def require_role(*roles: Role) -> Callable[..., Any]:
    allowed = {r.value for r in roles}

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in allowed:
                raise ForbiddenError(
                    code="AUTH_FORBIDDEN",
                    message_id="Anda tidak memiliki akses",
                    message_en="You do not have access to this resource",
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator
