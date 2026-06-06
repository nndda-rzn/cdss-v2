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
import { useI18nStore } from "@/lib/i18n/store";

import type { DuplicateSuggestion } from "../types";

interface DedupDialogProps {
  duplicates: DuplicateSuggestion[] | null;
  onClose: () => void;
  /** Proceed with registration despite the duplicate warning. */
  onConfirmNew: () => void;
}

/** Surfaces similar-patient matches; lets the registrar pick one or force-new. */
export function DedupDialog({ duplicates, onClose, onConfirmNew }: DedupDialogProps) {
  const navigate = useNavigate();
  const t = useI18nStore((s) => s.t);
  return (
    <Dialog open={duplicates !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t("Pasien Serupa Ditemukan", "Similar Patients Found")}</DialogTitle>
          <DialogDescription>
            {t(
              "Sistem menemukan pasien dengan nama, tanggal lahir, dan jenis kelamin yang serupa.",
              "The system found patients with similar name, date of birth, and gender.",
            )}
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
            {t("Daftarkan sebagai pasien baru", "Register as new patient")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

DedupDialog.displayName = "DedupDialog";
