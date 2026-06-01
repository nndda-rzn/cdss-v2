import { useAuthStore } from "@/features/auth/store";

import type { JwtClaims } from "../types";

export function getRoleFromToken(token: string | null): string | null {
  if (!token) return null;
  try {
    const payload = token.split(".")[1];
    const decoded = JSON.parse(atob(payload)) as JwtClaims;
    return decoded.role ?? null;
  } catch {
    return null;
  }
}

export function useRole(): string | null {
  const accessToken = useAuthStore((s) => s.accessToken);
  return getRoleFromToken(accessToken);
}

export function RoleGate({ allow, children }: { allow: string[]; children: React.ReactNode }) {
  const role = useRole();
  if (!role || !allow.includes(role)) {
    return null;
  }
  return <>{children}</>;
}
