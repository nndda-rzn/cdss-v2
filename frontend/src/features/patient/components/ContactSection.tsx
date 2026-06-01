import type { Control } from "react-hook-form";

import { Input } from "@/components/ui/input";
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { useI18nStore } from "@/lib/i18n/store";

import type { PatientCreateValues } from "../schemas";

interface ContactSectionProps {
  control: Control<PatientCreateValues>;
}

/** Optional-contact fields: phone, address. */
export function ContactSection({ control }: ContactSectionProps) {
  const t = useI18nStore((s) => s.t);

  return (
    <section className="space-y-4">
      <h2 className="section-label">{t("Kontak Opsional", "Optional Contact")}</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormField
          control={control}
          name="phone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t("Telepon", "Phone")}</FormLabel>
              <FormControl>
                <Input inputMode="tel" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={control}
          name="address"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t("Alamat", "Address")}</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </section>
  );
}
