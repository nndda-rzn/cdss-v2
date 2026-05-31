"""Import all models so Alembic autogenerate and create_all see them."""
from app.db.models.audit_log import AuditLog
from app.db.models.clinical_context import ClinicalContext
from app.db.models.consent import Consent
from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.facility import HealthcareFacility
from app.db.models.model_metadata import ModelMetadata
from app.db.models.patient import Patient
from app.db.models.patient_history import PatientHistory
from app.db.models.phi_access_log import PHIAccessLog
from app.db.models.refresh_token import RefreshToken
from app.db.models.system_config import SystemConfig
from app.db.models.user import User
from app.db.models.vital_signs import VitalSigns

__all__ = [
    "HealthcareFacility",
    "User",
    "RefreshToken",
    "AuditLog",
    "PHIAccessLog",
    "SystemConfig",
    "Patient",
    "PatientHistory",
    "Consent",
    "Encounter",
    "ClinicalContext",
    "VitalSigns",
    "ECGStudy",
    "ModelMetadata",
]
