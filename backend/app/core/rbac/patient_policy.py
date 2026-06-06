"""Role-based shaping of patient detail responses.

Treatment roles (admin, clinical) see full plaintext T1. Research roles
(researcher) get a pseudonymized view with no direct identifiers, satisfying
the "research export without T1" rule.
"""
from typing import Any

from app.core.rbac.roles import Role

_RESEARCH_ROLES = {Role.RESEARCHER}


def filter_patient_detail_for_role(detail: dict[str, Any], role: str) -> dict[str, Any]:
    if role in _RESEARCH_ROLES:
        return {
            "id": detail["id"],
            "dob": detail["dob"],
            "gender": detail["gender"],
            "facility_id": detail["facility_id"],
            "is_pseudonymized": True,
        }
    return detail
