import { useCallback, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useDropzone } from "react-dropzone";
import { ImageUp, UploadCloud, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useI18nStore } from "@/lib/i18n/store";
import { cn } from "@/lib/utils";

import { ecgKeys, uploadEcgStudy } from "../api";

const _ALLOWED = ["image/jpeg", "image/png"];
const _MAX_BYTES = 10 * 1024 * 1024;

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function EcgUploadForm({
  encounterId,
  onUploadSuccess,
}: {
  encounterId: string;
  onUploadSuccess?: () => void;
}) {
  const t = useI18nStore((s) => s.t);
  const qc = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const accept = useCallback((f: File) => {
    setError(null);
    if (!_ALLOWED.includes(f.type)) {
      setError(t("Format harus JPEG atau PNG", "Format must be JPEG or PNG"));
      setFile(null);
      setPreview(null);
      return;
    }
    if (f.size > _MAX_BYTES) {
      setError(t("Berkas melebihi 10 MB", "File exceeds 10 MB"));
      setFile(null);
      setPreview(null);
      return;
    }
    setFile(f);
    setPreview(URL.createObjectURL(f));
  }, []);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    accept: { "image/jpeg": [], "image/png": [] },
    maxSize: _MAX_BYTES,
    multiple: false,
    noClick: true,
    noKeyboard: true,
    onDropAccepted: (files) => files[0] && accept(files[0]),
    onDropRejected: () =>
      setError(
        t(
          "Berkas ditolak: pastikan JPEG/PNG dan maks 10 MB",
          "File rejected: ensure JPEG/PNG and max 10 MB",
        ),
      ),
  });

  const mutation = useMutation({
    mutationFn: () => {
      if (!file) throw new Error(t("Tidak ada berkas", "No file selected"));
      return uploadEcgStudy(encounterId, file);
    },
    onSuccess: () => {
      setFile(null);
      setPreview(null);
      setError(null);
      qc.invalidateQueries({ queryKey: ecgKeys.list(encounterId) });
      onUploadSuccess?.();
    },
    onError: (err) =>
      setError(err instanceof Error ? err.message : t("Gagal mengunggah", "Upload failed")),
  });

  function clearFile() {
    setFile(null);
    setPreview(null);
    setError(null);
  }

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className={cn(
          "flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed px-6 py-6 text-center transition-colors",
          isDragActive
            ? "border-primary bg-affirmed-soft"
            : "border-border-strong bg-sunken hover:bg-affirmed-soft/50",
        )}
      >
        <div className="rounded-full bg-primary/10 p-2">
          <UploadCloud className="h-6 w-6 text-primary shrink-0" aria-hidden="true" />
        </div>
        <div className="text-sm">
          <span className="font-medium text-foreground block">
            {t("Seret berkas EKG ke sini", "Drag ECG file here")}
          </span>
          <span className="text-xs text-muted-foreground mt-0.5 block">
            {t("JPEG/PNG, maks 10 MB", "JPEG/PNG, max 10 MB")}
          </span>
        </div>
        <Button
          type="button"
          variant="outline"
          className="w-full max-w-[220px] cursor-pointer mt-1"
          onClick={open}
        >
          <ImageUp className="mr-1.5 h-4 w-4" aria-hidden="true" />
          {t("Pilih berkas", "Choose file")}
        </Button>
        {/* The label keeps the accessible name for tests + a11y. */}
        <label htmlFor="ecg-file" className="sr-only">
          {t("Pilih berkas EKG", "Choose ECG file")}
        </label>
        <input id="ecg-file" {...getInputProps()} />
      </div>

      {preview && file && (
        <div className="flex items-center gap-3 rounded-lg border border-border-strong bg-card p-3">
          <img
            src={preview}
            alt={t("Pratinjau EKG", "ECG preview")}
            className="h-10 w-10 rounded-md object-cover"
          />
          <div className="flex flex-1 flex-col gap-0.5 text-sm min-w-0">
            <span className="truncate font-medium text-foreground">{file.name}</span>
            <span className="tabular text-xs text-muted-foreground">
              {formatBytes(file.size)} • {file.type.replace("image/", "").toUpperCase()}
            </span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8 cursor-pointer text-muted-foreground hover:text-destructive"
              onClick={clearFile}
              aria-label={t("Hapus berkas terpilih", "Remove selected file")}
            >
              <X className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              disabled={!file || mutation.isPending}
              onClick={() => mutation.mutate()}
              className="cursor-pointer"
            >
              {mutation.isPending ? t("Mengunggah...", "Uploading...") : t("Unggah", "Upload")}
            </Button>
          </div>
        </div>
      )}

      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  );
}
