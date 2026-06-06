const ACCESS = "ekg.access";
const REFRESH = "ekg.refresh";

export function saveTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS, access);
  localStorage.setItem(REFRESH, refresh);
}

export function loadTokens(): {
  accessToken: string | null;
  refreshToken: string | null;
} {
  return {
    accessToken: localStorage.getItem(ACCESS),
    refreshToken: localStorage.getItem(REFRESH),
  };
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS);
  localStorage.removeItem(REFRESH);
}

const REMEMBER = "ekg.remember";

export function saveRememberMe(value: boolean): void {
  localStorage.setItem(REMEMBER, String(value));
}

export function loadRememberMe(): boolean {
  return localStorage.getItem(REMEMBER) === "true";
}
