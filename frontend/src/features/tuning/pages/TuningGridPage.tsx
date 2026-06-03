// frontend/src/features/tuning/pages/TuningGridPage.tsx
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { ArrowLeft, LayoutGrid, Table } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { useI18nStore } from "@/lib/i18n/store";
import { fetchTuningGrid, tuningKeys } from "../api";
import { ActiveConfigPanel } from "../components/ActiveConfigPanel";
import { ConfigCard } from "../components/ConfigCard";
import { ConfigDetailModal } from "../components/ConfigDetailModal";
import { SummaryTable } from "../components/SummaryTable";
import type { TuningConfig } from "../types";

type ViewMode = "grid" | "table";

export function TuningGridPage() {
  const t = useI18nStore((s) => s.t);
  const [viewMode, setViewMode] = useState<ViewMode>("grid");
  const [selected, setSelected] = useState<TuningConfig | null>(null);

  const {
    data: configs,
    isLoading,
    error,
  } = useQuery({
    queryKey: tuningKeys.grid(),
    queryFn: fetchTuningGrid,
  });

  if (isLoading) {
    return (
      <div className="space-y-5">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {Array.from({ length: 12 }).map((_, i) => (
            <Skeleton key={i} className="aspect-square" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !configs) {
    return (
      <EmptyState
        title={t("Gagal memuat data", "Failed to load data")}
        description={t(
          "Terjadi kesalahan saat memuat hasil tuning",
          "An error occurred while loading tuning results",
        )}
      />
    );
  }

  if (configs.length === 0) {
    return (
      <EmptyState
        title={t("Belum ada hasil tuning", "No tuning results yet")}
        description={t(
          "Jalankan tuning pipeline untuk menghasilkan data",
          "Run the tuning pipeline to generate data",
        )}
      />
    );
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link to="/dashboard">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">
          {t("Hasil Tuning HiResCAM", "HiResCAM Tuning Results")}
        </h1>
        <div className="ml-auto flex gap-2">
          <Button
            variant={viewMode === "grid" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("grid")}
          >
            <LayoutGrid className="h-4 w-4 mr-1" />
            Grid
          </Button>
          <Button
            variant={viewMode === "table" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("table")}
          >
            <Table className="h-4 w-4 mr-1" />
            Table
          </Button>
        </div>
      </div>

      {/* Active production configuration */}
      <ActiveConfigPanel />

      {/* Content */}
      {viewMode === "grid" ? (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {configs.map((config) => (
            <ConfigCard key={config.config_index} config={config} onClick={setSelected} />
          ))}
        </div>
      ) : (
        <SummaryTable configs={configs} onSelect={setSelected} />
      )}

      {/* Detail Modal */}
      <ConfigDetailModal
        config={selected}
        open={selected !== null}
        onOpenChange={(open) => {
          if (!open) setSelected(null);
        }}
      />
    </div>
  );
}
