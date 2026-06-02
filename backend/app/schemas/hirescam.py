"""HiResCAMArtifact DTOs."""
from pydantic import BaseModel


class HiResCAMArtifactOut(BaseModel):
    id: int
    ai_analysis_id: int
    heatmap_path: str
    overlay_path: str
    side_by_side_path: str
    explanation_status: str
    focus_metric: float
    colormap_used: str
    generated_at: str
