// frontend/src/features/tuning/components/ConfigCard.tsx
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { tuningImageUrl } from "../api";
import type { TuningConfig } from "../types";

interface ConfigCardProps {
  config: TuningConfig;
  onClick: (config: TuningConfig) => void;
}

const statusColors: Record<string, string> = {
  good: "bg-green-100 text-green-800",
  diffuse: "bg-yellow-100 text-yellow-800",
  "off-target": "bg-red-100 text-red-800",
  "low-confidence": "bg-gray-100 text-gray-800",
};

export function ConfigCard({ config, onClick }: ConfigCardProps) {
  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => onClick(config)}
    >
      <CardContent className="p-3">
        <div className="aspect-square overflow-hidden rounded-md mb-2 bg-muted">
          <img
            src={tuningImageUrl(config.config_index, "overlay.png")}
            alt={`Config ${config.config_index}`}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </div>
        <div className="space-y-1 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-mono text-muted-foreground">#{config.config_index}</span>
            <Badge variant="secondary" className={statusColors[config.explanation_status] ?? ""}>
              {config.explanation_status}
            </Badge>
          </div>
          <div className="text-muted-foreground">
            {config.input_size} | {config.target_layer}
          </div>
          <div className="font-medium">focus: {config.focus_metric.toFixed(3)}</div>
        </div>
      </CardContent>
    </Card>
  );
}
