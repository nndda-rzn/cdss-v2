import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ExplanationStatusBadge } from "../components/ExplanationStatusBadge";

describe("ExplanationStatusBadge", () => {
  it("renders good status with focus metric", () => {
    render(<ExplanationStatusBadge status="good" focusMetric={0.85} />);
    expect(screen.getByText("Baik")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
  });

  it("renders off-target status", () => {
    render(<ExplanationStatusBadge status="off-target" />);
    expect(screen.getByText("Tidak Fokus")).toBeInTheDocument();
  });

  it("renders low-confidence status", () => {
    render(<ExplanationStatusBadge status="low-confidence" />);
    expect(screen.getByText("Keyakinan Rendah")).toBeInTheDocument();
  });
});
