import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore } from "./store";
import { loadTokens } from "@/lib/api/auth-token";

describe("auth store", () => {
  beforeEach(() => {
    useAuthStore.getState().clear();
  });

  it("sets and clears tokens", () => {
    useAuthStore.getState().setTokens("acc", "ref");
    expect(useAuthStore.getState().accessToken).toBe("acc");
    expect(useAuthStore.getState().refreshToken).toBe("ref");
    useAuthStore.getState().clear();
    expect(useAuthStore.getState().accessToken).toBeNull();
  });

  it("persists tokens to storage so they survive a reload", () => {
    useAuthStore.getState().setTokens("acc", "ref");
    expect(loadTokens()).toEqual({ accessToken: "acc", refreshToken: "ref" });
    useAuthStore.getState().clear();
    expect(loadTokens()).toEqual({ accessToken: null, refreshToken: null });
  });
});
