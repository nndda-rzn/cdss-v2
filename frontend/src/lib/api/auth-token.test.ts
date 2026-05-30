import { describe, it, expect, beforeEach } from "vitest";
import { saveTokens, loadTokens, clearTokens } from "./auth-token";

describe("auth-token persistence", () => {
  beforeEach(() => localStorage.clear());

  it("saves and loads tokens", () => {
    saveTokens("acc", "ref");
    expect(loadTokens()).toEqual({ accessToken: "acc", refreshToken: "ref" });
  });

  it("clears tokens", () => {
    saveTokens("acc", "ref");
    clearTokens();
    expect(loadTokens()).toEqual({ accessToken: null, refreshToken: null });
  });
});
