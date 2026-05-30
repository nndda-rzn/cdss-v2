import { describe, it, expect, beforeEach, vi } from "vitest";
import { apiFetch } from "./client";
import { useAuthStore } from "@/features/auth/store";

describe("apiFetch", () => {
  beforeEach(() => useAuthStore.getState().setTokens("acc", "ref"));

  it("attaches the access token", async () => {
    const spy = vi.fn<[RequestInfo | URL, RequestInit?], Promise<Response>>(
      async () => new Response(JSON.stringify({ ok: true }), { status: 200 }),
    );
    vi.stubGlobal("fetch", spy);
    await apiFetch("/api/test");
    const headers = (spy.mock.calls[0][1] as RequestInit).headers as Record<string, string>;
    expect(headers["Authorization"]).toBe("Bearer acc");
  });

  it("refreshes once on 401 then retries", async () => {
    const responses = [
      new Response("{}", { status: 401 }),
      new Response(JSON.stringify({ access_token: "new", refresh_token: "newref" }), {
        status: 200,
      }),
      new Response(JSON.stringify({ ok: true }), { status: 200 }),
    ];
    const spy = vi.fn(async () => responses.shift()!);
    vi.stubGlobal("fetch", spy);
    const resp = await apiFetch("/api/protected");
    expect(resp.status).toBe(200);
    expect(useAuthStore.getState().accessToken).toBe("new");
    expect(spy).toHaveBeenCalledTimes(3);
  });
});
