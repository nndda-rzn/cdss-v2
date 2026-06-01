import { Link } from "react-router-dom";
import { ClipboardPlus, Stethoscope, UserPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useI18nStore } from "@/lib/i18n/store";

/** Three-button quick-actions strip rendered on the dashboard. */
export function QuickActions() {
  const t = useI18nStore((s) => s.t);

  return (
    <div className="flex flex-wrap gap-2">
      <Button asChild size="sm" className="cursor-pointer">
        <Link to="/patients/new">
          <UserPlus className="mr-1.5 h-4 w-4" aria-hidden="true" />
          {t("Pasien Baru", "New Patient")}
        </Link>
      </Button>
      <Button asChild size="sm" variant="outline" className="cursor-pointer">
        <Link to="/patients">
          <Stethoscope className="mr-1.5 h-4 w-4" aria-hidden="true" />
          {t("Kunjungan Baru", "New Encounter")}
        </Link>
      </Button>
      <Button asChild size="sm" variant="ghost" className="cursor-pointer">
        <Link to="/patients">
          <ClipboardPlus className="mr-1.5 h-4 w-4" aria-hidden="true" />
          {t("Unggah EKG", "Upload ECG")}
        </Link>
      </Button>
    </div>
  );
}
