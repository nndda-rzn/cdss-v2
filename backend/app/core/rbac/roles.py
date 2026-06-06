"""Role definitions with backward compatibility mapping."""
from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    CLINICAL = "clinical"
    RESEARCHER = "researcher"


# Legacy role names → current role names
ROLE_ALIASES: dict[str, str] = {
    "clinician": "clinical",
    "nurse": "clinical",
    "expert_reviewer": "researcher",
}


def resolve_role(role: str) -> str:
    """Resolve legacy role names to current roles."""
    return ROLE_ALIASES.get(role, role)
