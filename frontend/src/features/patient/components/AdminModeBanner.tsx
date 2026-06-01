import { ShieldAlert } from "lucide-react";

import { useRole } from "@/features/auth/components/RoleGate";
import { useI18nStore } from "@/lib/i18n/store";

/**
 * One-line advisory banner shown only to admin users on the patient list.
 * Patient registration / encounter creation are clinician/nurse-only
 * (ADR-0006 separation of duties), so admins see this instead of write
 * buttons. Renders null for every other role.
 */
export function AdminModeBanner() {
  const role = useRole();
  const t = useI18nStore((s) => s.t);

  if (role !== "admin") return null;

  return (
    <div
      role="note"
      className="flex items-start gap-2 rounded-md border border-amber-500/30 bg-caution-soft px-3 py-2 text-xs text-amber-700"
    >
      <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <span>
        {t(
          "Mode admin — pendaftaran pasien hanya tersedia untuk klinisi atau perawat.",
          "Admin mode — patient registration is available to clinicians or nurses only.",
        )}
      </span>
    </div>
  );
}
