import { useAuthStore } from "@/features/auth/store";

async function doRefresh(): Promise<boolean> {
  const { refreshToken } = useAuthStore.getState();
  if (!refreshToken) return false;
  const resp = await fetch("/api/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!resp.ok) {
    useAuthStore.getState().clear();
    return false;
  }
  const data = await resp.json();
  useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
  return true;
}

export async function apiFetch(url: string, init: RequestInit = {}): Promise<Response> {
  const { accessToken } = useAuthStore.getState();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  let resp = await fetch(url, { ...init, headers });
  if (resp.status === 401 && (await doRefresh())) {
    const retryToken = useAuthStore.getState().accessToken;
    if (retryToken) headers["Authorization"] = `Bearer ${retryToken}`;
    resp = await fetch(url, { ...init, headers });
  }
  return resp;
}
