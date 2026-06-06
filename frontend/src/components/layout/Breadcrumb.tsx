import { Link, useLocation, useParams } from "react-router-dom";
import { ChevronRight } from "lucide-react";

import { cn } from "@/lib/utils";

interface Crumb {
  label: string;
  href?: string;
}

/**
 * Path-driven breadcrumb that derives crumbs from the current URL.
 * Returns null when there is nothing meaningful to render (e.g. /dashboard root).
 *
 * Recognised paths:
 *   /patients                                 -> Pasien
 *   /patients/new                             -> Pasien > Daftar baru
 *   /patients/:id                             -> Pasien > Detail
 *   /patients/:id/encounters/new              -> Pasien > Detail > Kunjungan baru
 *   /encounters/:id                           -> Kunjungan #:id
 */
function deriveCrumbs(pathname: string, params: Record<string, string | undefined>): Crumb[] {
  if (pathname === "/dashboard") return [];

  if (pathname === "/admin") return [{ label: "Admin" }];
  if (pathname === "/admin/users") {
    return [{ label: "Admin", href: "/admin" }, { label: "User" }];
  }
  if (pathname === "/admin/facilities") {
    return [{ label: "Admin", href: "/admin" }, { label: "Fasilitas" }];
  }

  if (pathname === "/patients") return [{ label: "Pasien" }];
  if (pathname === "/patients/new") {
    return [{ label: "Pasien", href: "/patients" }, { label: "Daftar baru" }];
  }

  if (pathname.startsWith("/patients/") && pathname.endsWith("/encounters/new")) {
    const pid = params.id ?? "";
    return [
      { label: "Pasien", href: "/patients" },
      { label: "Detail", href: `/patients/${pid}` },
      { label: "Kunjungan baru" },
    ];
  }

  if (pathname.startsWith("/patients/")) {
    return [{ label: "Pasien", href: "/patients" }, { label: "Detail" }];
  }

  if (pathname.startsWith("/encounters/")) {
    return [{ label: `Kunjungan #${params.id ?? ""}` }];
  }

  return [];
}

export function Breadcrumb({ className }: { className?: string }) {
  const { pathname } = useLocation();
  const params = useParams();
  const crumbs = deriveCrumbs(pathname, params);

  if (crumbs.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className={cn("text-xs text-muted-foreground", className)}>
      <ol className="flex flex-wrap items-center gap-1">
        {crumbs.map((c, i) => {
          const isLast = i === crumbs.length - 1;
          return (
            <li key={`${c.label}-${i}`} className="flex items-center gap-1">
              {c.href && !isLast ? (
                <Link to={c.href} className="hover:text-foreground hover:underline">
                  {c.label}
                </Link>
              ) : (
                <span className={cn(isLast && "text-foreground")}>{c.label}</span>
              )}
              {!isLast && <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

Breadcrumb.displayName = "Breadcrumb";
