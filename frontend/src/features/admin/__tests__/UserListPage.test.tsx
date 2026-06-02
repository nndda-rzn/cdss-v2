import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { UserListPage } from "../pages/UserListPage";

vi.mock("../api", () => ({
  fetchUsers: vi.fn(),
  createUser: vi.fn(),
  updateUser: vi.fn(),
  adminKeys: { users: ["admin", "users"] },
}));

import { fetchUsers } from "../api";

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <UserListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("UserListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders heading", async () => {
    vi.mocked(fetchUsers).mockResolvedValue({ items: [] });
    renderPage();
    expect(await screen.findByRole("heading", { name: /user/i })).toBeInTheDocument();
  });

  it("shows user rows", async () => {
    vi.mocked(fetchUsers).mockResolvedValue({
      items: [
        {
          id: 1,
          name: "Admin",
          email: "adm@test.local",
          role: "admin",
          facility_id: 1,
          is_active: true,
          profession: null,
          license_number: null,
        },
      ],
    });
    renderPage();
    expect(await screen.findByText("Admin")).toBeInTheDocument();
    expect(screen.getByText("adm@test.local")).toBeInTheDocument();
  });
});
