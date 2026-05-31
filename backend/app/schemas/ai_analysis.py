"""AIAnalysis DTOs."""
from pydantic import BaseModel


class AIAnalysisOut(BaseModel):
    id: int
    ecg_study_id: int
    model_metadata_id: int
    model_name: str
    architecture: str
    predicted_class: str | None = None
    confidence_score: float | None = None
    probability_json: dict[str, object]
    inference_time_ms: int | None = None
    device_used: str
    status: str
    error_message: str | None = None
    created_at: str
