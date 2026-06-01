import { Languages } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

/** Compact ID/EN switch shown in the app header. */
export function LanguageToggle({ className }: { className?: string }) {
  const lang = useI18nStore((s) => s.lang);
  const toggle = useI18nStore((s) => s.toggle);

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggle}
      className={cn("h-8 cursor-pointer gap-1.5 px-2 text-xs font-medium uppercase", className)}
      aria-label={lang === "id" ? "Ganti bahasa ke Inggris" : "Switch language to Indonesian"}
      title={lang === "id" ? "Ganti ke EN" : "Switch to ID"}
    >
      <Languages className="h-4 w-4" aria-hidden="true" />
      <span className="tabular">{lang}</span>
    </Button>
  );
}
