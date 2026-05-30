"""RBAC roles."""
from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    CLINICIAN = "clinician"
    NURSE = "nurse"
    RESEARCHER = "researcher"
    EXPERT_REVIEWER = "expert_reviewer"
