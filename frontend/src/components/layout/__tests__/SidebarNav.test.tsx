import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";

import { useAuthStore } from "@/features/auth/store";

import { SidebarNav } from "../SidebarNav";

function tokenWithRole(role: string): string {
  const payload = btoa(JSON.stringify({ role }));
  return `header.${payload}.sig`;
}

describe("SidebarNav", () => {
  beforeEach(() => {
    useAuthStore.getState().clear();
  });

  it("does not keep admin dashboard active on nested admin routes", () => {
    useAuthStore.setState({ accessToken: tokenWithRole("admin") });
    render(
      <MemoryRouter initialEntries={["/admin/users"]}>
        <SidebarNav />
      </MemoryRouter>,
    );

    expect(screen.getByRole("link", { name: /dashboard/i })).not.toHaveAttribute("aria-current");
    expect(screen.getByRole("link", { name: /user/i })).toHaveAttribute("aria-current", "page");
  });
});
