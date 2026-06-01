import { apiFetch } from "@/lib/api/client";

import type { SearchResults } from "./types";

export type { EncounterHit, PatientHit, SearchResults } from "./types";

export async function fetchSearch(q: string): Promise<SearchResults> {
  const resp = await apiFetch(`/api/search?q=${encodeURIComponent(q)}`);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat pencarian");
  return body as SearchResults;
}
