import { TriangleAlert, XCircle, Plus } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useI18nStore } from "@/lib/i18n/store";

interface EncounterActionsCardProps {
  status: string;
  patientId: string;
  closing: boolean;
  onClose: () => void;
}

/** Rail card: close-encounter action with a short clinical hint. */
export function EncounterActionsCard({ status, patientId, closing, onClose }: EncounterActionsCardProps) {
  const t = useI18nStore((s) => s.t);

  const handleClose = () => {
    const confirmMessage = t(
      "Apakah Anda yakin ingin menutup kunjungan ini? Data kunjungan tidak akan dapat diubah lagi setelah ditutup.",
      "Are you sure you want to close this encounter? The encounter data cannot be modified after it is closed.",
    );
    if (window.confirm(confirmMessage)) {
      onClose();
    }
  };

  return (
    <Card>
      <CardHeader className="p-4 pb-2" sectionLabel={t("Aksi", "Actions")} />
      <CardContent className="p-4 pt-0">
        {status === "open" ? (
          <div className="space-y-2">
            <p className="flex items-start gap-1.5 text-xs text-amber-700">
              <TriangleAlert className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
              {t(
                "Tutup kunjungan setelah pemeriksaan selesai untuk membekukan data.",
                "Close the encounter after the exam is done to freeze the record.",
              )}
            </p>
            <Button
              variant="outline"
              disabled={closing}
              onClick={handleClose}
              className="w-full cursor-pointer"
            >
              <XCircle className="mr-1.5 h-4 w-4" aria-hidden="true" />
              {closing ? t("Menutup...", "Closing...") : t("Tutup Kunjungan", "Close Encounter")}
            </Button>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">
              {t("Kunjungan telah ditutup.", "This encounter has been closed.")}
            </p>
            <Button asChild variant="outline" className="w-full cursor-pointer">
              <Link to={`/patients/${patientId}/encounters/new`}>
                <Plus className="mr-1.5 h-4 w-4" aria-hidden="true" />
                {t("Kunjungan Baru", "New Encounter")}
              </Link>
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
