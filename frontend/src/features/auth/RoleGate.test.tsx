import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { RoleGate, getRoleFromToken } from "./RoleGate";
import { useAuthStore } from "./store";

function tokenWithRole(role: string): string {
  const payload = btoa(JSON.stringify({ role }));
  return `header.${payload}.sig`;
}

describe("getRoleFromToken", () => {
  it("extracts role from a JWT payload", () => {
    expect(getRoleFromToken(tokenWithRole("admin"))).toBe("admin");
  });

  it("returns null for null token", () => {
    expect(getRoleFromToken(null)).toBeNull();
  });

  it("returns null for malformed token", () => {
    expect(getRoleFromToken("not-a-jwt")).toBeNull();
  });
});

describe("RoleGate", () => {
  beforeEach(() => {
    useAuthStore.getState().clear();
  });

  it("renders children when role is allowed", () => {
    useAuthStore.setState({ accessToken: tokenWithRole("admin") });
    render(
      <RoleGate allow={["admin"]}>
        <button>Hapus</button>
      </RoleGate>,
    );
    expect(screen.getByRole("button", { name: /hapus/i })).toBeInTheDocument();
  });

  it("hides children when role is not allowed", () => {
    useAuthStore.setState({ accessToken: tokenWithRole("clinician") });
    render(
      <RoleGate allow={["admin"]}>
        <button>Hapus</button>
      </RoleGate>,
    );
    expect(screen.queryByRole("button", { name: /hapus/i })).toBeNull();
  });
});
