import { LogOut, User } from "lucide-react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { logout } from "@/features/auth/api";
import { useAuthStore } from "@/features/auth/store";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

interface JwtClaims {
  sub?: string;
  role?: string;
  facility_id?: number;
  email?: string;
}

/** Decode a JWT payload without verifying the signature (display-only use). */
function decode(token: string | null): JwtClaims {
  if (!token) return {};
  const parts = token.split(".");
  if (parts.length !== 3) return {};
  try {
    const padded = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(padded.padEnd(padded.length + ((4 - (padded.length % 4)) % 4), "="));
    return JSON.parse(json) as JwtClaims;
  } catch {
    return {};
  }
}

const ROLE_LABEL_ID: Record<string, string> = {
  admin: "Admin",
  clinician: "Klinisi",
  nurse: "Perawat",
  researcher: "Peneliti",
  superadmin: "Super Admin",
};
const ROLE_LABEL_EN: Record<string, string> = {
  admin: "Admin",
  clinician: "Clinician",
  nurse: "Nurse",
  researcher: "Researcher",
  superadmin: "Super Admin",
};

/** Avatar dropdown shown in the right side of the header. */
export function UserMenu() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const t = useI18nStore((s) => s.t);

  const claims = decode(accessToken);
  const role = claims.role ?? "user";
  const roleLabel = t(ROLE_LABEL_ID[role] ?? role, ROLE_LABEL_EN[role] ?? role);
  const initial = (claims.email ?? role ?? "?").charAt(0).toUpperCase();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          aria-label={t("Menu pengguna", "User menu")}
          className={cn(
            "flex h-8 w-8 cursor-pointer items-center justify-center rounded-full",
            "bg-affirmed-soft text-xs font-semibold text-primary",
            "ring-2 ring-transparent transition-all hover:ring-primary/30",
            "focus-visible:outline-none focus-visible:ring-primary",
          )}
        >
          {initial}
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel className="flex flex-col gap-0.5">
          <span className="text-sm font-semibold text-foreground">{roleLabel}</span>
          {claims.email && (
            <span className="truncate text-xs font-normal text-muted-foreground">
              {claims.email}
            </span>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem disabled className="text-xs text-muted-foreground">
          <User className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
          {t("Profil (segera)", "Profile (soon)")}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => logout()} className="cursor-pointer text-destructive">
          <LogOut className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
          {t("Keluar", "Sign out")}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
