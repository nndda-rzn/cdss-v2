import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
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
import { DedupDialog } from "./DedupDialog";
import { PatientCreateSchema, type DuplicateSuggestion, type PatientCreateValues } from "./schemas";
import { registerPatient } from "./api";

export function RegisterForm() {
  const navigate = useNavigate();
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
    <div className="max-w-lg">
      <h1 className="mb-4 text-xl font-semibold">Pasien Baru</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit((v) => submit(v))} className="space-y-4">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Nama Lengkap</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="dob"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Tanggal Lahir</FormLabel>
                <FormControl>
                  <Input type="date" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="gender"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Jenis Kelamin</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="male">Laki-laki</SelectItem>
                    <SelectItem value="female">Perempuan</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="nik"
            render={({ field }) => (
              <FormItem>
                <FormLabel>NIK (opsional)</FormLabel>
                <FormControl>
                  <Input inputMode="numeric" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="phone"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Telepon (opsional)</FormLabel>
                <FormControl>
                  <Input inputMode="tel" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="address"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Alamat (opsional)</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="consent_data_use"
            render={({ field }) => (
              <FormItem>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={field.value}
                    onChange={(e) => field.onChange(e.target.checked)}
                  />
                  Pasien menyetujui penggunaan data untuk pelayanan
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
          <Button type="submit" disabled={form.formState.isSubmitting}>
            Daftar
          </Button>
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
    </div>
  );
}
