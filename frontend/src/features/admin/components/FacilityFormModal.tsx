import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { AdminFacility } from "../types";

interface Props {
  open: boolean;
  onClose: () => void;
  onSave: (data: Record<string, unknown>) => void;
  facility?: AdminFacility | null;
}

const FACILITY_TYPES = ["puskesmas", "rs_pratama", "rs_utama", "rs_khusus", "klinik", "lab"];

export function FacilityFormModal({ open, onClose, onSave, facility }: Props) {
  const { register, handleSubmit, reset, setValue, watch } = useForm({
    defaultValues: {
      name: "",
      code: "",
      facility_type: "puskesmas",
      address: "",
      province_code: "",
      regency_code: "",
      subdistrict_code: "",
    },
  });

  useEffect(() => {
    if (facility) {
      reset({
        name: facility.name,
        code: facility.code,
        facility_type: facility.facility_type,
        address: facility.address ?? "",
        province_code: facility.province_code ?? "",
        regency_code: facility.regency_code ?? "",
        subdistrict_code: facility.subdistrict_code ?? "",
      });
    } else {
      reset({
        name: "",
        code: "",
        facility_type: "puskesmas",
        address: "",
        province_code: "",
        regency_code: "",
        subdistrict_code: "",
      });
    }
  }, [facility, reset]);

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{facility ? "Edit Fasilitas" : "Tambah Fasilitas"}</DialogTitle>
          <DialogDescription>
            {facility ? "Ubah data fasilitas." : "Buat fasilitas baru."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSave)} className="space-y-3">
          <div>
            <Label htmlFor="fac-name">Nama</Label>
            <Input id="fac-name" {...register("name", { required: true })} />
          </div>
          <div>
            <Label htmlFor="fac-code">Kode</Label>
            <Input id="fac-code" {...register("code", { required: true })} disabled={!!facility} />
          </div>
          <div>
            <Label>Tipe</Label>
            <Select
              value={watch("facility_type")}
              onValueChange={(v) => setValue("facility_type", v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {FACILITY_TYPES.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="fac-address">Alamat</Label>
            <Input id="fac-address" {...register("address")} />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Batal
            </Button>
            <Button type="submit">Simpan</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
