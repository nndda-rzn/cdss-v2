import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Home } from "lucide-react";

import { EcgSweep } from "@/components/brand/EcgSweep";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store";
import { useI18nStore } from "@/lib/i18n/store";

/**
 * Custom 404 page rendered for any unmatched authenticated path. Picks up the
 * EcgSweep brand motif and offers two recovery actions: back to dashboard,
 * or back to the previous page in history.
 */
export function NotFoundRoute() {
  const t = useI18nStore((s) => s.t);
  const navigate = useNavigate();
  const accessToken = useAuthStore((s) => s.accessToken);
  const home = accessToken ? "/dashboard" : "/login";

  return (
    <main className="relative flex min-h-screen items-center justify-center bg-sunken px-4 py-10">
      <EcgSweep
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-primary/[0.05]"
        width={900}
        height={240}
        thickness={3}
      />
      <div className="relative z-10 flex max-w-md flex-col items-center gap-4 text-center">
        <span className="rounded-md bg-affirmed-soft px-3 py-1 text-xs font-semibold uppercase tracking-wide text-primary">
          404
        </span>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          {t("Halaman tidak ditemukan", "Page not found")}
        </h1>
        <p className="text-sm text-muted-foreground">
          {t(
            "Halaman yang Anda cari mungkin telah dipindahkan atau tidak pernah ada.",
            "The page you're looking for may have moved or never existed.",
          )}
        </p>
        <div className="mt-2 flex flex-wrap items-center justify-center gap-2">
          <Button asChild className="cursor-pointer">
            <Link to={home}>
              <Home className="mr-1.5 h-4 w-4" aria-hidden="true" />
              {accessToken
                ? t("Kembali ke Dashboard", "Back to Dashboard")
                : t("Halaman masuk", "Sign-in page")}
            </Link>
          </Button>
          <Button variant="outline" onClick={() => navigate(-1)} className="cursor-pointer">
            <ArrowLeft className="mr-1.5 h-4 w-4" aria-hidden="true" />
            {t("Halaman sebelumnya", "Previous page")}
          </Button>
        </div>
      </div>
    </main>
  );
}
