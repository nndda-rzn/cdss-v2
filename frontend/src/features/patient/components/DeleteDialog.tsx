import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
    onError: (err) => setError(err instanceof Error ? err.message : "Gagal menghapus"),
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="destructive">Hapus Pasien</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Hapus Pasien</DialogTitle>
          <DialogDescription>
            Tindakan ini menandai pasien sebagai terhapus. Berikan alasan penghapusan.
          </DialogDescription>
        </DialogHeader>
        <Input
          aria-label="Alasan penghapusan"
          placeholder="Alasan penghapusan (wajib)"
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
            Konfirmasi Hapus
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
