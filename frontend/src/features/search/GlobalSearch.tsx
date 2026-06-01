import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";

import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import { fetchSearch } from "./api";
import { useDebouncedValue } from "./hooks";
import { SearchResultList } from "./SearchResultList";

interface GlobalSearchProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

/**
 * Command-palette dialog. Open with Ctrl+K (registered by `GlobalSearchTrigger`
 * which renders the input button in the header). The dialog itself is dumb —
 * it focuses an input, debounces the query, and renders the results list.
 */
export function GlobalSearch({ open, onOpenChange }: GlobalSearchProps) {
  const t = useI18nStore((s) => s.t);
  const [q, setQ] = useState("");
  const debounced = useDebouncedValue(q, 250);
  const enabled = open && debounced.trim().length >= 2;

  const { data, isFetching } = useQuery({
    queryKey: ["search", debounced],
    queryFn: () => fetchSearch(debounced),
    enabled,
    staleTime: 10_000,
  });

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (!next) setQ("");
        onOpenChange(next);
      }}
    >
      <DialogContent
        className={cn("max-w-xl gap-0 p-0 sm:rounded-lg")}
        aria-label={t("Pencarian global", "Global search")}
      >
        <DialogTitle className="sr-only">{t("Pencarian", "Search")}</DialogTitle>
        <div className="flex items-center gap-2 border-b border-border px-3 py-3">
          <Search className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={t(
              "Cari pasien (MRN), keluhan utama...",
              "Search patients (MRN), chief complaint...",
            )}
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            aria-label={t("Kueri pencarian", "Search query")}
          />
          <kbd className="hidden rounded-sm border border-border-strong bg-sunken px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground sm:inline">
            Esc
          </kbd>
        </div>
        <div className="max-h-[60vh] overflow-y-auto">
          <SearchResultList
            patients={data?.patients ?? []}
            encounters={data?.encounters ?? []}
            query={debounced}
            loading={isFetching && enabled}
            onPick={() => {
              setQ("");
              onOpenChange(false);
            }}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
