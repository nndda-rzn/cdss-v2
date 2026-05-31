import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import * as api from "./api";
import { AnalysisPanel } from "./AnalysisPanel";

function renderWithClient(ui: React.ReactNode) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("AnalysisPanel", () => {
  it("renders the comparison table with architectures and predicted labels", async () => {
    vi.spyOn(api, "fetchAnalyses").mockResolvedValue([
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
        created_at: "2026-05-31T10:00:00",
      },
      {
        id: 2,
        ecg_study_id: 10,
        model_metadata_id: 2,
        model_name: "yolov8s-cls",
        architecture: "YOLOv8s",
        predicted_class: "normal",
        confidence_score: 0.81,
        probability_json: { abnormal: 0.05, homi: 0.07, mi: 0.07, normal: 0.81 },
        inference_time_ms: 110,
        device_used: "cpu",
        status: "success",
        error_message: null,
        created_at: "2026-05-31T10:00:01",
      },
    ]);

    renderWithClient(<AnalysisPanel encounterId="1" studyId="10" />);

    expect(await screen.findByText("YOLOv8n")).toBeInTheDocument();
    expect(screen.getByText("YOLOv8s")).toBeInTheDocument();
    expect(screen.getAllByText(/infark|normal/i).length).toBeGreaterThan(0);
  });
});
