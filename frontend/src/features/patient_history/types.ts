/** Public domain types for the patient-history feature. */

export interface HistoryRow {
  id: number;
  condition_code: string;
  onset_date_approx: string | null;
  note: string | null;
  recorded_at: string;
}
