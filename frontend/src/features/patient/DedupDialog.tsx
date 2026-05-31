import { useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import type { DuplicateSuggestion } from "./schemas";

interface DedupDialogProps {
  duplicates: DuplicateSuggestion[] | null;
  onClose: () => void;
  /** Proceed with registration despite the duplicate warning. */
  onConfirmNew: () => void;
}

/** Surfaces similar-patient matches; lets the registrar pick one or force-new. */
export function DedupDialog({ duplicates, onClose, onConfirmNew }: DedupDialogProps) {
  const navigate = useNavigate();
  return (
    <Dialog open={duplicates !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Pasien Serupa Ditemukan</DialogTitle>
          <DialogDescription>
            Sistem menemukan pasien dengan nama, tanggal lahir, dan jenis kelamin yang serupa.
          </DialogDescription>
        </DialogHeader>
        <ul className="space-y-2">
          {duplicates?.map((d) => (
            <li key={d.id} className="rounded-md border p-3 text-sm">
              <button
                type="button"
                className="text-left"
                onClick={() => navigate(`/patients/${d.id}`)}
              >
                <span className="font-medium">{d.name_masked}</span>
                <br />
                {d.mrn} | {d.dob} | {d.gender}
              </button>
            </li>
          ))}
        </ul>
        <DialogFooter>
          <Button variant="outline" onClick={onConfirmNew}>
            Daftarkan sebagai pasien baru
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

DedupDialog.displayName = "DedupDialog";
