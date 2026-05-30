import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore } from "./store";

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
});
