"""ECGStudy DTOs."""
from pydantic import BaseModel


class ECGStudyOut(BaseModel):
    id: int
    encounter_id: int
    patient_id: str
    study_uid: str
    image_original_path: str
    image_processed_path: str | None = None
    image_quality_status: str
    image_quality_score: float
    image_quality_metrics_json: dict[str, object]
    acquired_at: str
    recorded_by_user_id: int
    device_info: str | None = None
    created_at: str
