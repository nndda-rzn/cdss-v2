import { apiFetch } from "@/lib/api/client";

import { useAuthStore } from "./store";
import type { AuthUser, LoginInput } from "./types";

export type { AuthUser, JwtClaims, LoginInput } from "./types";

export async function login(input: LoginInput): Promise<{ role: string }> {
  const resp = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!resp.ok) {
    const body = await resp.json();
    throw new Error(body.error?.message_en ?? "Login failed");
  }
  const data = await resp.json();
  useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
  return { role: data.user.role };
}

export async function fetchMe(): Promise<AuthUser> {
  const resp = await apiFetch("/api/auth/me");
  const data = await resp.json();
  return data.user;
}

export async function logout(): Promise<void> {
  const { refreshToken } = useAuthStore.getState();
  if (refreshToken) {
    try {
      await apiFetch("/api/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } catch {
      // Best-effort: even if revoke fails, clear local state
    }
  }
  useAuthStore.getState().clear();
}
