import { useNavigate } from "react-router-dom";

import { EcgSweep } from "@/components/brand/EcgSweep";
import { LanguageToggle } from "@/components/layout/LanguageToggle";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoginForm } from "@/features/auth/LoginForm";
import { useI18nStore } from "@/lib/i18n/store";

export function LoginRoute() {
  const navigate = useNavigate();
  const t = useI18nStore((s) => s.t);

  return (
    <main
      className="relative flex min-h-screen items-center justify-center px-4"
      style={{
        // Soft radial gradient instead of flat sunken — adds the SaaS feel
        // without leaving the petrol palette. Clinical, not consumer.
        background:
          "radial-gradient(circle at 20% 0%, hsl(192 50% 96%) 0%, transparent 55%)," +
          "radial-gradient(circle at 80% 100%, hsl(192 50% 94%) 0%, transparent 50%)," +
          "hsl(var(--sunken))",
      }}
    >
      <EcgSweep
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-primary/[0.05]"
        width={900}
        height={240}
        thickness={3}
      />

      <div className="absolute right-4 top-4 z-20">
        <LanguageToggle />
      </div>

      <Card className="relative z-10 w-full max-w-sm shadow-elev-lg">
        <CardHeader className="items-center text-center">
          <div className="mb-1 flex items-center justify-center gap-2 text-primary">
            <EcgSweep width={36} height={18} thickness={2.5} />
          </div>
          <CardTitle className="text-lg">EKG-Insight</CardTitle>
          <p className="text-xs text-muted-foreground">
            {t("Sistem Pendukung Keputusan Klinis", "Clinical Decision Support System")}
          </p>
        </CardHeader>
        <CardContent>
          <LoginForm onSuccess={() => navigate("/dashboard")} />
        </CardContent>
      </Card>
    </main>
  );
}
