"""Access token helper. JWT signing key comes from app config (env), NOT master.key."""
from typing import cast

from flask_jwt_extended import create_access_token


def make_access_token(*, user_id: int, role: str, facility_id: int) -> str:
    return cast(str, create_access_token(
        identity=str(user_id),
        additional_claims={"role": role, "facility_id": facility_id},
    ))
