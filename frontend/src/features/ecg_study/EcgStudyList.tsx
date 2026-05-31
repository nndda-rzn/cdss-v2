import { useQuery } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { ecgKeys, fetchEcgStudies, type EcgStudyRow } from "./api";

const _STATUS_LABEL: Record<EcgStudyRow["image_quality_status"], string> = {
  good: "Baik",
  acceptable: "Cukup",
  poor: "Buruk",
};

const _STATUS_VARIANT: Record<
  EcgStudyRow["image_quality_status"],
  "default" | "secondary" | "destructive"
> = {
  good: "default",
  acceptable: "secondary",
  poor: "destructive",
};

export function EcgStudyList({ encounterId }: { encounterId: string }) {
  const { data } = useQuery({
    queryKey: ecgKeys.list(encounterId),
    queryFn: () => fetchEcgStudies(encounterId),
  });

  if (!data || data.length === 0) {
    return <p className="text-sm text-muted-foreground">Belum ada studi EKG.</p>;
  }

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b text-left">
          <th className="py-1">Study UID</th>
          <th className="py-1">Kualitas</th>
          <th className="py-1">Skor</th>
          <th className="py-1">Waktu</th>
        </tr>
      </thead>
      <tbody>
        {data.map((s) => (
          <tr key={s.id} className="border-b">
            <td className="py-1 font-mono text-xs">{s.study_uid}</td>
            <td className="py-1">
              <Badge variant={_STATUS_VARIANT[s.image_quality_status]}>
                {_STATUS_LABEL[s.image_quality_status]}
              </Badge>
            </td>
            <td className="py-1">{s.image_quality_score.toFixed(2)}</td>
            <td className="py-1">{s.created_at.slice(0, 16)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
