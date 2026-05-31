import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import * as api from "./api";
import { EcgStudyList } from "./EcgStudyList";

function renderWithClient(ui: React.ReactNode) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("EcgStudyList", () => {
  it("renders quality badge for a study", async () => {
    vi.spyOn(api, "fetchEcgStudies").mockResolvedValue([
      {
        id: 1,
        encounter_id: 1,
        study_uid: "ECG-P1-x-abcd",
        image_original_path: "uploads/ecg/1/1/ECG-P1-x-abcd.jpg",
        image_processed_path: null,
        image_quality_status: "good",
        image_quality_score: 0.85,
        image_quality_metrics_json: {},
        acquired_at: "2026-05-31T10:00:00",
        recorded_by_user_id: 1,
        created_at: "2026-05-31T10:00:00",
      },
    ]);
    renderWithClient(<EcgStudyList encounterId="1" />);
    expect(await screen.findByText(/baik/i)).toBeInTheDocument();
    expect(screen.getByText("ECG-P1-x-abcd")).toBeInTheDocument();
  });
});
