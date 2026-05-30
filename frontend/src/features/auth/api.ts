import { apiFetch } from "@/lib/api/client";
import { useAuthStore } from "./store";

export interface LoginInput {
  email: string;
  password: string;
}

export async function login(input: LoginInput): Promise<void> {
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
}

export async function fetchMe(): Promise<{
  id: number;
  name: string;
  role: string;
}> {
  const resp = await apiFetch("/api/auth/me");
  const data = await resp.json();
  return data.user;
}
