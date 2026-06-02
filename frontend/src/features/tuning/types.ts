// frontend/src/features/tuning/types.ts
export interface TuningConfig {
  config_index: number;
  input_size: number;
  target_layer: string;
  smooth_sigma: number;
  top_percent: number;
  clip_percentile: number;
  colormap: string;
  explanation_status: string;
  focus_metric: number;
  confidence: number;
}

export interface TuningMetadata extends TuningConfig {
  image_path: string;
  original_size: [number, number];
  target_layer_info: string;
  target_class_id: number;
  letterbox_ratio: number;
  letterbox_padding: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  overlay_alpha: number;
}
