import { useNavigate } from "react-router-dom";

import { EcgSweep } from "@/components/brand/EcgSweep";
import { LanguageToggle } from "@/components/layout/LanguageToggle";
import { LoginBrandPanel } from "@/features/auth/LoginBrandPanel";
import { LoginForm } from "@/features/auth/LoginForm";
import { useI18nStore } from "@/lib/i18n/store";

/**
 * Clinical split-screen login (2026-06-01-clinical-split-login-design.md).
 * Left: dark petrol brand panel with the EcgSweep watermark (lg+ only).
 * Right: clean white form panel hosting the existing `LoginForm`.
 */
export function LoginRoute() {
  const navigate = useNavigate();
  const t = useI18nStore((s) => s.t);

  return (
    <main className="grid min-h-screen bg-paper lg:grid-cols-2">
      <LoginBrandPanel />

      <section className="relative flex items-center justify-center px-6 py-10">
        <div className="absolute right-4 top-4 z-20">
          <LanguageToggle />
        </div>

        <div className="w-full max-w-sm">
          {/* Mobile/tablet brand block — replaces the hidden left panel. */}
          <div className="mb-6 flex flex-col items-center gap-2 text-center lg:hidden">
            <EcgSweep className="text-primary" width={36} height={18} thickness={2.5} />
            <h1 className="text-lg font-semibold tracking-tight">EKG-Insight</h1>
            <p className="text-xs text-muted-foreground">
              {t("Sistem Pendukung Keputusan Klinis", "Clinical Decision Support System")}
            </p>
          </div>

          {/* Desktop welcome block — mirrors the brand panel's tone. */}
          <div className="mb-5 hidden flex-col gap-1 lg:flex">
            <h2 className="text-xl font-semibold tracking-tight">
              {t("Selamat datang", "Welcome back")}
            </h2>
            <p className="text-sm text-muted-foreground">
              {t("Masuk dengan akun klinik Anda.", "Sign in with your facility account.")}
            </p>
          </div>

          <LoginForm onSuccess={() => navigate("/dashboard")} />
        </div>
      </section>
    </main>
  );
}
