import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { useAuthStore } from "../store";

function renderAt(initial: string) {
  return render(
    <MemoryRouter initialEntries={[initial]}>
      <Routes>
        <Route path="/login" element={<div>Login Page</div>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => useAuthStore.getState().clear());

  it("redirects to login when unauthenticated", () => {
    renderAt("/dashboard");
    expect(screen.getByText("Login Page")).toBeInTheDocument();
  });

  it("renders child when authenticated", () => {
    useAuthStore.getState().setTokens("acc", "ref");
    renderAt("/dashboard");
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });
});
