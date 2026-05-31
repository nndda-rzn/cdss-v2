import { useState } from "react";
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
import { createEncounter } from "./api";

const EncounterSchema = z.object({
  encounter_type: z.enum(["rawat_jalan", "igd"]),
  chief_complaint: z.string().optional(),
});

type EncounterValues = z.infer<typeof EncounterSchema>;

export function CreateForm() {
  const { id: patientId = "" } = useParams();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);
  const form = useForm<EncounterValues>({
    resolver: zodResolver(EncounterSchema),
    defaultValues: { encounter_type: "rawat_jalan", chief_complaint: "" },
  });

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
      <h1 className="mb-4 text-xl font-semibold">Kunjungan Baru</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="encounter_type"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Tipe Kunjungan</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="rawat_jalan">Rawat Jalan</SelectItem>
                    <SelectItem value="igd">IGD</SelectItem>
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
                <FormLabel>Keluhan Utama</FormLabel>
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
            Buat Kunjungan
          </Button>
        </form>
      </Form>
    </div>
  );
}
