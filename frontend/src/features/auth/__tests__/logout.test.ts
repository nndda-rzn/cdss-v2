import { describe, it, expect, vi, beforeEach } from "vitest";
import { logout } from "../api";
import { useAuthStore } from "../store";

vi.mock("@/lib/api/client", () => ({
  apiFetch: vi.fn(async () => new Response(JSON.stringify({ status: "ok" }), { status: 200 })),
}));

describe("logout", () => {
  beforeEach(() => {
    useAuthStore.getState().setTokens("acc", "ref");
  });

  it("calls backend logout endpoint then clears local state", async () => {
    const { apiFetch } = await import("@/lib/api/client");
    await logout();
    expect(apiFetch).toHaveBeenCalledWith("/api/auth/logout", {
      method: "POST",
      body: JSON.stringify({ refresh_token: "ref" }),
    });
    expect(useAuthStore.getState().accessToken).toBeNull();
    expect(useAuthStore.getState().refreshToken).toBeNull();
  });

  it("clears local state even if backend call fails", async () => {
    vi.mocked((await import("@/lib/api/client")).apiFetch).mockRejectedValueOnce(
      new Error("network"),
    );
    await logout();
    expect(useAuthStore.getState().accessToken).toBeNull();
  });
});
