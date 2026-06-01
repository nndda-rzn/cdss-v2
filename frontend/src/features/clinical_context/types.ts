/** Public domain types for the clinical-context feature. */

export interface ClinicalContextOut {
  id: number;
  encounter_id: number;
  symptom_chest_pain: boolean;
  symptom_dyspnea: boolean;
  symptom_palpitation: boolean;
  symptom_syncope: boolean;
  symptom_other: string | null;
  pain_onset_minutes: number | null;
  pain_duration_minutes: number | null;
}

export interface ClinicalContextInput {
  symptom_chest_pain: boolean;
  symptom_dyspnea: boolean;
  symptom_palpitation: boolean;
  symptom_syncope: boolean;
  symptom_other?: string;
  pain_onset_minutes?: number;
}
