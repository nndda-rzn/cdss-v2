/** Public domain types for the vital-signs feature. */

export interface VitalRow {
  id: number;
  measured_at: string;
  bp_systolic: number | null;
  bp_diastolic: number | null;
  heart_rate: number | null;
  respiratory_rate: number | null;
  spo2: number | null;
  temperature: number | null;
  weight: number | null;
  height: number | null;
}

export type VitalsInput = Partial<Omit<VitalRow, "id" | "measured_at">>;
