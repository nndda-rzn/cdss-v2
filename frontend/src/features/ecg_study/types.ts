/** Public domain types for the ECG-study feature. */

export type ImageQualityStatus = "good" | "acceptable" | "poor";

export interface EcgStudyRow {
  id: number;
  encounter_id: number;
  patient_id?: string;
  study_uid: string;
  image_original_path: string;
  image_processed_path: string | null;
  image_quality_status: ImageQualityStatus;
  image_quality_score: number;
  image_quality_metrics_json: Record<string, number>;
  acquired_at: string;
  recorded_by_user_id: number;
  device_info?: string | null;
  created_at: string;
}
