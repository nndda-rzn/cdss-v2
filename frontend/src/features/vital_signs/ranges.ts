/**
 * Clinical range classification for vital signs.
 * Pure domain logic — no React, independently testable.
 */
import type { VitalRow } from "./types";

export type VitalStatus = "ok" | "caution" | "negative" | "unknown";

export interface VitalStatuses {
  bp: VitalStatus;
  hr: VitalStatus;
  spo2: VitalStatus;
  temp: VitalStatus;
  resp: VitalStatus;
}

function classifyBp(sys: number | null, dia: number | null): VitalStatus {
  if (sys === null || dia === null) return "unknown";
  if (sys >= 180 || dia >= 110 || sys < 90) return "negative";
  if (sys >= 140 || dia >= 90) return "caution";
  return "ok";
}

function classifyHr(hr: number | null): VitalStatus {
  if (hr === null) return "unknown";
  if (hr < 50 || hr > 130) return "negative";
  if (hr < 60 || hr > 100) return "caution";
  return "ok";
}

function classifySpo2(spo2: number | null): VitalStatus {
  if (spo2 === null) return "unknown";
  if (spo2 < 90) return "negative";
  if (spo2 < 95) return "caution";
  return "ok";
}

function classifyTemp(temp: number | null): VitalStatus {
  if (temp === null) return "unknown";
  if (temp < 35 || temp >= 39) return "negative";
  if (temp >= 38) return "caution";
  return "ok";
}

function classifyResp(resp: number | null): VitalStatus {
  if (resp === null) return "unknown";
  if (resp < 10 || resp > 30) return "negative";
  if (resp > 24) return "caution";
  return "ok";
}

export function classify(latest: VitalRow): VitalStatuses {
  return {
    bp: classifyBp(latest.bp_systolic, latest.bp_diastolic),
    hr: classifyHr(latest.heart_rate),
    spo2: classifySpo2(latest.spo2),
    temp: classifyTemp(latest.temperature),
    resp: classifyResp(latest.respiratory_rate),
  };
}
