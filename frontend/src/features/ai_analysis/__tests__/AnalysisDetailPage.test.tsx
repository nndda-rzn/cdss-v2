import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import * as analysisApi from "../api";
import * as ecgApi from "@/features/ecg_study/api";
import { AnalysisDetailPage } from "../pages/AnalysisDetailPage";

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={["/encounters/1/ecg-studies/10/analyses"]}>
        <Routes>
          <Route
            path="/encounters/:id/ecg-studies/:studyId/analyses"
            element={<AnalysisDetailPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("AnalysisDetailPage", () => {
  it("renders the comparison table with architectures and consensus", async () => {
    vi.spyOn(ecgApi, "fetchEcgStudy").mockResolvedValue({
      id: 10,
      encounter_id: 1,
      study_uid: "ECG-P1-x-abcd",
      image_original_path: "uploads/ecg/1/10/ECG-P1-x-abcd.jpg",
      image_processed_path: null,
      image_quality_status: "acceptable",
      image_quality_score: 0.64,
      image_quality_metrics_json: {},
      acquired_at: "2026-06-01T10:26:00",
      recorded_by_user_id: 1,
      created_at: "2026-06-01T10:26:00",
    });
    vi.spyOn(analysisApi, "fetchAnalyses").mockResolvedValue([
      {
        id: 1,
        ecg_study_id: 10,
        model_metadata_id: 1,
        model_name: "yolov8n-cls",
        architecture: "YOLOv8n",
        predicted_class: "mi",
        confidence_score: 0.92,
        probability_json: { abnormal: 0.02, homi: 0.03, mi: 0.92, normal: 0.03 },
        inference_time_ms: 93,
        device_used: "cpu",
        status: "success",
        error_message: null,
        created_at: "2026-06-01T10:26:01",
      },
    ]);

    renderPage();

    expect(await screen.findByText("YOLOv8n")).toBeInTheDocument();
    expect(screen.getAllByText(/konsensus|consensus/i).length).toBeGreaterThan(0);
  });

  it("renders an access-denied state when analyses query fails", async () => {
    vi.spyOn(ecgApi, "fetchEcgStudy").mockRejectedValue(new Error("403"));
    vi.spyOn(analysisApi, "fetchAnalyses").mockRejectedValue(new Error("403"));

    renderPage();

    expect(await screen.findByText(/akses ditolak|access denied/i)).toBeInTheDocument();
  });
});
