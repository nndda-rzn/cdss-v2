import { ShieldCheck } from "lucide-react";

import { EcgSweep } from "@/components/brand/EcgSweep";
import { useI18nStore } from "@/lib/i18n/store";

/**
 * Dark petrol panel rendered on the left half of the login screen at lg+.
 * Pure presentation: brand wordmark, sub-headline, trust line + disclaimer,
 * and an oversized EcgSweep watermark behind everything. Hidden below lg.
 */
export function LoginBrandPanel() {
  const t = useI18nStore((s) => s.t);

  return (
    <aside className="relative hidden flex-col justify-between overflow-hidden bg-petrol-900 px-10 py-10 text-white lg:flex">
      <EcgSweep
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-white/[0.06]"
        width={900}
        height={240}
        thickness={3}
      />

      <header className="relative z-10 flex items-center gap-2">
        <EcgSweep className="text-white" width={36} height={18} thickness={2.5} />
        <span className="text-base font-semibold tracking-tight">CardioVision-CDSS</span>
      </header>

      <div className="relative z-10 flex max-w-md flex-col gap-4">
        <h1 className="text-3xl font-semibold leading-tight tracking-tight text-white">
          {t("Sistem Pendukung Keputusan Klinis", "Clinical Decision Support System")}
        </h1>
        <p className="text-sm leading-relaxed text-white/75">
          {t(
            "Analisis EKG berbasis AI untuk membantu klinisi mengambil keputusan triage yang lebih cepat dan terstandar.",
            "AI-assisted ECG analysis to help clinicians make faster, more standardized triage decisions.",
          )}
        </p>
      </div>

      <footer className="relative z-10 flex items-start gap-2 text-xs leading-relaxed text-white/60">
        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        <span>
          {t(
            "Akses aman untuk tenaga kesehatan. Hasil AI bersifat membantu — keputusan klinis tetap di tangan dokter.",
            "Secure access for healthcare professionals. AI output is advisory — clinical decisions remain with the clinician.",
          )}
        </span>
      </footer>
    </aside>
  );
}
