import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useI18nStore } from "@/lib/i18n/store";

interface EncounterInfoCardProps {
  encounterType: string;
  startedAt: string;
  chiefComplaint: string | null;
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3 border-b border-border py-1.5 last:border-0">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-right text-foreground">{value}</span>
    </div>
  );
}

/** Rail card: encounter metadata (type, start, chief complaint). */
export function EncounterInfoCard({
  encounterType,
  startedAt,
  chiefComplaint,
}: EncounterInfoCardProps) {
  const t = useI18nStore((s) => s.t);
  const typeLabel = encounterType === "igd" ? "IGD" : t("Rawat Jalan", "Outpatient");

  return (
    <Card>
      <CardHeader className="p-4 pb-2" sectionLabel={t("Info Kunjungan", "Encounter Info")} />
      <CardContent className="p-4 pt-0 text-sm">
        <Row label={t("Tipe", "Type")} value={typeLabel} />
        <Row label={t("Mulai", "Started")} value={startedAt.slice(0, 16).replace("T", " ")} />
        <Row label={t("Keluhan Utama", "Chief Complaint")} value={chiefComplaint ?? "-"} />
      </CardContent>
    </Card>
  );
}
