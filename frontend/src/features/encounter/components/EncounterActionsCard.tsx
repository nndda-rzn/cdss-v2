import { TriangleAlert, XCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useI18nStore } from "@/lib/i18n/store";

interface EncounterActionsCardProps {
  status: string;
  closing: boolean;
  onClose: () => void;
}

/** Rail card: close-encounter action with a short clinical hint. */
export function EncounterActionsCard({ status, closing, onClose }: EncounterActionsCardProps) {
  const t = useI18nStore((s) => s.t);

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
              onClick={onClose}
              className="w-full cursor-pointer"
            >
              <XCircle className="mr-1.5 h-4 w-4" aria-hidden="true" />
              {closing ? t("Menutup...", "Closing...") : t("Tutup Kunjungan", "Close Encounter")}
            </Button>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground">
            {t("Kunjungan telah ditutup.", "This encounter has been closed.")}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
