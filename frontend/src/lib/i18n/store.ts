/**
 * Bilingual UI store (ID/EN) per ADR-0012.
 *
 * Defaults to Indonesian. Persists the user's choice in localStorage so the
 * preference survives reloads. Components consume `t(idStr, enStr)` for
 * inline translation, keeping strings adjacent to the markup that uses them.
 */
import { create } from "zustand";

export type Language = "id" | "en";

const STORAGE_KEY = "ekg.lang";

function loadLang(): Language {
  if (typeof window === "undefined") return "id";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored === "en" ? "en" : "id";
}

function saveLang(lang: Language) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, lang);
}

interface I18nState {
  lang: Language;
  setLang: (lang: Language) => void;
  toggle: () => void;
  t: (idStr: string, enStr: string) => string;
}

export const useI18nStore = create<I18nState>((set, get) => ({
  lang: loadLang(),
  setLang: (lang) => {
    saveLang(lang);
    set({ lang });
  },
  toggle: () => {
    const next = get().lang === "id" ? "en" : "id";
    saveLang(next);
    set({ lang: next });
  },
  t: (idStr, enStr) => (get().lang === "id" ? idStr : enStr),
}));

/** Stable hook that returns just the translator + current lang. */
export function useT() {
  const lang = useI18nStore((s) => s.lang);
  const t = useI18nStore((s) => s.t);
  return { lang, t };
}
