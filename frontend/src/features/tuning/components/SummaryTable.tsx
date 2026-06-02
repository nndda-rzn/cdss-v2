// frontend/src/features/tuning/components/SummaryTable.tsx
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { TuningConfig } from "../types";

interface SummaryTableProps {
  configs: TuningConfig[];
  onSelect: (config: TuningConfig) => void;
}

export function SummaryTable({ configs, onSelect }: SummaryTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Summary ({configs.length} experiments)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">#</th>
                <th className="text-left p-2">Input</th>
                <th className="text-left p-2">Layer</th>
                <th className="text-left p-2">Smooth</th>
                <th className="text-left p-2">Top%</th>
                <th className="text-left p-2">Colormap</th>
                <th className="text-left p-2">Focus</th>
                <th className="text-left p-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {configs.map((c) => (
                <tr
                  key={c.config_index}
                  className="border-b hover:bg-muted cursor-pointer"
                  onClick={() => onSelect(c)}
                >
                  <td className="p-2 font-mono">{c.config_index}</td>
                  <td className="p-2">{c.input_size}</td>
                  <td className="p-2">{c.target_layer}</td>
                  <td className="p-2">{c.smooth_sigma}</td>
                  <td className="p-2">{c.top_percent}</td>
                  <td className="p-2">{c.colormap}</td>
                  <td className="p-2 font-medium">{c.focus_metric.toFixed(3)}</td>
                  <td className="p-2">
                    <Badge variant="secondary">{c.explanation_status}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
