import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useI18nStore } from "@/lib/i18n/store";
import { createEncounter } from "../api";

const EncounterSchema = z.object({
  encounter_type: z.enum(["rawat_jalan", "igd"]),
  chief_complaint: z.string().optional(),
});

type EncounterValues = z.infer<typeof EncounterSchema>;

export function CreateForm() {
  const { id: patientId = "" } = useParams();
  const navigate = useNavigate();
  const t = useI18nStore((s) => s.t);
  const [serverError, setServerError] = useState<string | null>(null);
  const form = useForm<EncounterValues>({
    resolver: zodResolver(EncounterSchema),
    defaultValues: { encounter_type: "rawat_jalan", chief_complaint: "" },
  });

  const isDirty = form.formState.isDirty;
  const isSubmitting = form.formState.isSubmitting;

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty && !isSubmitting) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [isDirty, isSubmitting]);

  async function onSubmit(values: EncounterValues) {
    setServerError(null);
    try {
      const enc = await createEncounter({
        patient_id: patientId,
        encounter_type: values.encounter_type,
        chief_complaint: values.chief_complaint || undefined,
      });
      navigate(`/encounters/${enc.id}`);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Gagal");
    }
  }

  return (
    <div className="max-w-lg">
      <h1 className="mb-4 text-xl font-semibold">{t("Kunjungan Baru", "New Encounter")}</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="encounter_type"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("Tipe Kunjungan", "Encounter Type")}</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="rawat_jalan">{t("Rawat Jalan", "Outpatient")}</SelectItem>
                    <SelectItem value="igd">{t("IGD", "ER")}</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="chief_complaint"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("Keluhan Utama", "Chief Complaint")}</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          {serverError && (
            <p role="alert" className="text-sm text-destructive">
              {serverError}
            </p>
          )}
          <Button type="submit" disabled={form.formState.isSubmitting}>
            {form.formState.isSubmitting
              ? t("Membuat...", "Creating...")
              : t("Buat Kunjungan", "Create Encounter")}
          </Button>
        </form>
      </Form>
    </div>
  );
}
