/** Public domain types for the AI-analysis feature. */

export type PredictedClass = "normal" | "mi" | "homi" | "abnormal";

export type AnalysisStatus = "success" | "failed" | "skipped";

export interface AnalysisRow {
  id: number;
  ecg_study_id: number;
  model_metadata_id: number;
  model_name: string;
  architecture: string;
  predicted_class: PredictedClass | null;
  confidence_score: number | null;
  probability_json: Record<string, number>;
  inference_time_ms: number | null;
  device_used: string;
  status: AnalysisStatus;
  error_message: string | null;
  created_at: string;
}

export type ExplanationStatus =
  | "good"
  | "diffuse"
  | "off-target"
  | "low-confidence"
  | "need-review";

export interface ModelOption {
  id: number;
  model_name: string;
  model_version: string;
  architecture: string;
  is_active: boolean;
}

export interface HiResCAMRow {
  id: number;
  ai_analysis_id: number;
  heatmap_path: string;
  overlay_path: string;
  side_by_side_path: string;
  explanation_status: ExplanationStatus;
  focus_metric: number;
  colormap_used: string;
  generated_at: string;
}
