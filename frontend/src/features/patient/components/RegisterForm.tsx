import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { Form, FormField, FormItem, FormMessage } from "@/components/ui/form";
import { useI18nStore } from "@/lib/i18n/store";

import { registerPatient } from "../api";
import {
  PatientCreateSchema,
  type DuplicateSuggestion,
  type PatientCreateValues,
} from "../schemas";
import { ContactSection } from "./ContactSection";
import { DedupDialog } from "./DedupDialog";
import { IdentitySection } from "./IdentitySection";

/**
 * Patient register form — SaaS card + grid layout
 * (2026-06-01-saas-register-form-design.md). Sections live in their own
 * focused files; this component owns the form state machine, the page
 * chrome, and the action footer.
 */
export function RegisterForm() {
  const navigate = useNavigate();
  const t = useI18nStore((s) => s.t);
  const [serverError, setServerError] = useState<string | null>(null);
  const [duplicates, setDuplicates] = useState<DuplicateSuggestion[] | null>(null);
  const form = useForm<PatientCreateValues>({
    resolver: zodResolver(PatientCreateSchema),
    defaultValues: {
      name: "",
      dob: "",
      gender: "male",
      nik: "",
      phone: "",
      address: "",
      consent_data_use: false as unknown as true,
    },
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

  async function submit(values: PatientCreateValues, confirmNew = false) {
    setServerError(null);
    try {
      const result = await registerPatient(values, { confirmNew });
      if (result.action === "confirm" && result.duplicates) {
        setDuplicates(result.duplicates);
        return;
      }
      if (result.patient) {
        navigate(`/patients/${result.patient.id}`);
      }
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Registrasi gagal");
    }
  }

  return (
    <div className="flex justify-center pb-8">
      <Card className="w-full max-w-3xl">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl">{t("Pasien Baru", "New Patient")}</CardTitle>
          <p className="text-sm text-muted-foreground">
            {t(
              "Daftarkan pasien baru ke fasilitas Anda.",
              "Register a new patient to your facility.",
            )}
          </p>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit((v) => submit(v))} className="space-y-6">
              <IdentitySection control={form.control} />

              <Separator />

              <ContactSection control={form.control} />

              <Separator />

              <FormField
                control={form.control}
                name="consent_data_use"
                render={({ field }) => (
                  <FormItem>
                    <label className="flex items-start gap-2 text-sm">
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={(v) => field.onChange(v === true)}
                        className="mt-0.5"
                      />
                      <span>
                        {t(
                          "Pasien menyetujui penggunaan data untuk pelayanan",
                          "Patient consents to data use for clinical services",
                        )}
                      </span>
                    </label>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {serverError && (
                <p role="alert" className="text-sm text-destructive">
                  {serverError}
                </p>
              )}

              <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate(-1)}
                  className="cursor-pointer"
                >
                  <ArrowLeft className="mr-1.5 h-4 w-4" aria-hidden="true" />
                  {t("Batal", "Cancel")}
                </Button>
                <Button
                  type="submit"
                  disabled={form.formState.isSubmitting}
                  className="cursor-pointer"
                >
                  {t("Daftar", "Register")}
                </Button>
              </div>
            </form>
          </Form>

          <DedupDialog
            duplicates={duplicates}
            onClose={() => setDuplicates(null)}
            onConfirmNew={() => {
              setDuplicates(null);
              void submit(form.getValues(), true);
            }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
