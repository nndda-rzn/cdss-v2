"""Role-based shaping of patient detail responses.

Treatment roles (admin, clinician, nurse) see full plaintext T1. Research roles
(researcher, expert_reviewer) get a pseudonymized view with no direct
identifiers, satisfying the "research export without T1" rule.
"""
from typing import Any

_RESEARCH_ROLES = {"researcher", "expert_reviewer"}


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
