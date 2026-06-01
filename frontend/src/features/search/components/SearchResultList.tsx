import { useNavigate } from "react-router-dom";
import { Search, User2, Stethoscope } from "lucide-react";

import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import type { EncounterHit, PatientHit } from "../types";

interface ResultListProps {
  patients: PatientHit[];
  encounters: EncounterHit[];
  query: string;
  loading: boolean;
  onPick: () => void;
}

const TYPE_ID: Record<EncounterHit["encounter_type"], string> = {
  rawat_jalan: "Rawat Jalan",
  igd: "IGD",
};
const TYPE_EN: Record<EncounterHit["encounter_type"], string> = {
  rawat_jalan: "Outpatient",
  igd: "ER",
};

const ROW_BASE =
  "flex w-full cursor-pointer items-center gap-3 rounded-md px-3 py-2 text-left text-sm hover:bg-sunken focus-visible:bg-sunken focus-visible:outline-none";

export function SearchResultList({
  patients,
  encounters,
  query,
  loading,
  onPick,
}: ResultListProps) {
  const t = useI18nStore((s) => s.t);
  const navigate = useNavigate();

  if (loading) {
    return (
      <p className="px-3 py-6 text-center text-xs text-muted-foreground">
        {t("Mencari...", "Searching...")}
      </p>
    );
  }

  const hasQuery = query.trim().length >= 2;
  if (!hasQuery) {
    return (
      <p className="px-3 py-6 text-center text-xs text-muted-foreground">
        {t(
          "Ketik minimal 2 karakter untuk mencari pasien atau kunjungan.",
          "Type at least 2 characters to search patients or encounters.",
        )}
      </p>
    );
  }

  if (patients.length === 0 && encounters.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 px-3 py-8 text-center">
        <Search className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
        <p className="text-sm text-foreground">{t("Tidak ada hasil", "No results")}</p>
        <p className="text-xs text-muted-foreground">
          {t("Coba kata kunci lain atau MRN pasien.", "Try a different keyword or patient MRN.")}
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 py-2">
      {patients.length > 0 && (
        <div>
          <div className="px-3 pb-1 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
            {t("Pasien", "Patients")}
          </div>
          {patients.map((p) => (
            <button
              key={p.id}
              type="button"
              className={ROW_BASE}
              onClick={() => {
                navigate(`/patients/${p.id}`);
                onPick();
              }}
            >
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-affirmed-soft text-primary">
                <User2 className="h-4 w-4" aria-hidden="true" />
              </span>
              <div className="min-w-0 flex-1">
                <div className="truncate font-medium text-foreground">{p.name_masked ?? "-"}</div>
                <div className="tabular truncate text-xs text-muted-foreground">
                  {p.mrn} · {p.dob}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {encounters.length > 0 && (
        <div>
          <div className="px-3 pb-1 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
            {t("Kunjungan", "Encounters")}
          </div>
          {encounters.map((e) => (
            <button
              key={e.id}
              type="button"
              className={ROW_BASE}
              onClick={() => {
                navigate(`/encounters/${e.id}`);
                onPick();
              }}
            >
              <span
                className={cn(
                  "flex h-8 w-8 shrink-0 items-center justify-center rounded-md",
                  e.encounter_type === "igd"
                    ? "bg-negative-soft text-wine-700"
                    : "bg-affirmed-soft text-primary",
                )}
              >
                <Stethoscope className="h-4 w-4" aria-hidden="true" />
              </span>
              <div className="min-w-0 flex-1">
                <div className="truncate font-medium text-foreground">
                  {t(TYPE_ID[e.encounter_type], TYPE_EN[e.encounter_type])} · #
                  <span className="tabular">{e.id}</span>
                </div>
                <div className="truncate text-xs text-muted-foreground">
                  {e.chief_complaint ?? t("Tanpa keluhan utama", "No chief complaint")}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
