import type { Control } from "react-hook-form";

import { Input } from "@/components/ui/input";
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useI18nStore } from "@/lib/i18n/store";

import type { PatientCreateValues } from "../schemas";

interface IdentitySectionProps {
  control: Control<PatientCreateValues>;
}

/** Required-identity fields: name, dob, gender, NIK. */
export function IdentitySection({ control }: IdentitySectionProps) {
  const t = useI18nStore((s) => s.t);

  return (
    <section className="space-y-4">
      <h2 className="section-label">{t("Identitas Pasien", "Patient Identity")}</h2>
      <FormField
        control={control}
        name="name"
        render={({ field }) => (
          <FormItem>
            <FormLabel>{t("Nama Lengkap", "Full Name")}</FormLabel>
            <FormControl>
              <Input {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormField
          control={control}
          name="dob"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t("Tanggal Lahir", "Date of Birth")}</FormLabel>
              <FormControl>
                <Input type="date" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={control}
          name="gender"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t("Jenis Kelamin", "Gender")}</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="male">{t("Laki-laki", "Male")}</SelectItem>
                  <SelectItem value="female">{t("Perempuan", "Female")}</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
      <FormField
        control={control}
        name="nik"
        render={({ field }) => (
          <FormItem>
            <FormLabel>{t("NIK (opsional)", "NIK (optional)")}</FormLabel>
            <FormControl>
              <Input inputMode="numeric" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </section>
  );
}
