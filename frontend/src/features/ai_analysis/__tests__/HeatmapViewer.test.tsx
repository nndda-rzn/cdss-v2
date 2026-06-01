import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { HeatmapViewer } from "../components/HeatmapViewer";
import type { HiResCAMRow } from "../types";

vi.mock("@/components/ui/authed-image", () => ({
  AuthedImage: ({ alt }: { alt: string }) => <div data-testid="authed-image">{alt}</div>,
}));

vi.mock("react-medium-image-zoom", () => ({
  default: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

const mockArtifact: HiResCAMRow = {
  id: 1,
  ai_analysis_id: 1,
  heatmap_path: "heatmaps/1/heatmap.png",
  overlay_path: "heatmaps/1/overlay.png",
  side_by_side_path: "heatmaps/1/side_by_side.png",
  explanation_status: "good",
  focus_metric: 0.85,
  colormap_used: "inferno",
  generated_at: "2026-06-01T00:00:00Z",
};

describe("HeatmapViewer", () => {
  it("renders toggle buttons and focus metric", () => {
    render(<HeatmapViewer artifact={mockArtifact} originalPath="test.jpg" />);
    expect(screen.getByText("Heatmap")).toBeInTheDocument();
    expect(screen.getByText("Overlay")).toBeInTheDocument();
    expect(screen.getByText("Bandingkan")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
  });

  it("shows overlay image by default", () => {
    render(<HeatmapViewer artifact={mockArtifact} originalPath="test.jpg" />);
    const images = screen.getAllByTestId("authed-image");
    expect(images).toHaveLength(1);
    expect(images[0]).toHaveTextContent("Overlay Heatmap");
  });
});
