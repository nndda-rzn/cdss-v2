import { describe, expect, it } from "vitest";

import type { VitalRow } from "../types";
import { classify } from "../ranges";

function row(overrides: Partial<VitalRow>): VitalRow {
  return {
    id: 1,
    measured_at: "2026-05-31T10:00:00",
    bp_systolic: null,
    bp_diastolic: null,
    heart_rate: null,
    respiratory_rate: null,
    spo2: null,
    temperature: null,
    weight: null,
    height: null,
    ...overrides,
  };
}

describe("classify vital ranges", () => {
  it("flags hypertensive crisis as negative", () => {
    expect(classify(row({ bp_systolic: 185, bp_diastolic: 120 })).bp).toBe("negative");
  });

  it("flags stage-2 hypertension as caution", () => {
    expect(classify(row({ bp_systolic: 150, bp_diastolic: 95 })).bp).toBe("caution");
  });

  it("treats normal BP as ok", () => {
    expect(classify(row({ bp_systolic: 120, bp_diastolic: 80 })).bp).toBe("ok");
  });

  it("flags low SpO2 as negative", () => {
    expect(classify(row({ spo2: 88 })).spo2).toBe("negative");
  });

  it("flags fever as caution and high fever as negative", () => {
    expect(classify(row({ temperature: 38.2 })).temp).toBe("caution");
    expect(classify(row({ temperature: 39.5 })).temp).toBe("negative");
  });

  it("returns unknown when a field is absent", () => {
    const s = classify(row({}));
    expect(s.hr).toBe("unknown");
    expect(s.resp).toBe("unknown");
  });
});
