import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useI18nStore } from "@/lib/i18n/store";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { deletePatient, patientKeys } from "../api";

export function DeleteDialog({ patientId }: { patientId: string }) {
  const navigate = useNavigate();
  const t = useI18nStore((s) => s.t);
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => deletePatient(patientId, reason),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: patientKeys.all });
      navigate("/patients");
    },
    onError: (err) =>
      setError(err instanceof Error ? err.message : t("Gagal menghapus", "Delete failed")),
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="destructive">{t("Hapus Pasien", "Delete Patient")}</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t("Hapus Pasien", "Delete Patient")}</DialogTitle>
          <DialogDescription>
            {t(
              "Tindakan ini menandai pasien sebagai terhapus. Berikan alasan penghapusan.",
              "This action marks the patient as deleted. Provide a reason for deletion.",
            )}
          </DialogDescription>
        </DialogHeader>
        <Input
          aria-label={t("Alasan penghapusan", "Deletion reason")}
          placeholder={t("Alasan penghapusan (wajib)", "Deletion reason (required)")}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
        {error && (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
        <DialogFooter>
          <Button
            variant="destructive"
            disabled={!reason.trim() || mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            {t("Konfirmasi Hapus", "Confirm Delete")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
