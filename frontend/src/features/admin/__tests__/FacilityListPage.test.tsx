import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { FacilityListPage } from "../pages/FacilityListPage";

vi.mock("../api", () => ({
  fetchFacilities: vi.fn(),
  createFacility: vi.fn(),
  updateFacility: vi.fn(),
  adminKeys: { facilities: ["admin", "facilities"] },
}));

import { fetchFacilities } from "../api";

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <FacilityListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("FacilityListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders heading", async () => {
    vi.mocked(fetchFacilities).mockResolvedValue({ items: [] });
    renderPage();
    expect(await screen.findByRole("heading", { name: /fasilitas/i })).toBeInTheDocument();
  });

  it("shows facility rows", async () => {
    vi.mocked(fetchFacilities).mockResolvedValue({
      items: [
        {
          id: 1,
          name: "Pusk A",
          code: "P-A",
          facility_type: "puskesmas",
          address: null,
          province_code: null,
          regency_code: null,
          subdistrict_code: null,
          is_active: true,
        },
      ],
    });
    renderPage();
    expect(await screen.findByText("Pusk A")).toBeInTheDocument();
    expect(screen.getByText("P-A")).toBeInTheDocument();
  });
});
