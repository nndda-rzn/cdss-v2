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
import type { AdminUser } from "../types";

interface Props {
  open: boolean;
  onClose: () => void;
  onSave: (data: Record<string, unknown>) => void;
  user?: AdminUser | null;
}

const ROLES = ["admin", "clinician", "nurse", "researcher", "expert_reviewer"];

export function UserFormModal({ open, onClose, onSave, user }: Props) {
  const { register, handleSubmit, reset, setValue, watch } = useForm({
    defaultValues: {
      name: "",
      email: "",
      password: "",
      role: "clinician",
      facility_id: 1,
      profession: "",
      license_number: "",
    },
  });

  useEffect(() => {
    if (user) {
      reset({
        name: user.name,
        email: user.email,
        password: "",
        role: user.role,
        facility_id: user.facility_id,
        profession: user.profession ?? "",
        license_number: user.license_number ?? "",
      });
    } else {
      reset({
        name: "",
        email: "",
        password: "",
        role: "clinician",
        facility_id: 1,
        profession: "",
        license_number: "",
      });
    }
  }, [user, reset]);

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{user ? "Edit User" : "Tambah User"}</DialogTitle>
          <DialogDescription>
            {user ? "Ubah data pengguna." : "Buat pengguna baru."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSave)} className="space-y-3">
          <div>
            <Label htmlFor="name">Nama</Label>
            <Input id="name" {...register("name", { required: true })} />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              {...register("email", { required: true })}
              disabled={!!user}
            />
          </div>
          {!user && (
            <div>
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" {...register("password", { required: true })} />
            </div>
          )}
          <div>
            <Label>Role</Label>
            <Select value={watch("role")} onValueChange={(v) => setValue("role", v)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ROLES.map((r) => (
                  <SelectItem key={r} value={r}>
                    {r}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="profession">Profesi</Label>
            <Input id="profession" {...register("profession")} />
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
