import { useCallback, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useDropzone } from "react-dropzone";
import { ImageUp, UploadCloud, X } from "lucide-react";

import { Button } from "@/components/ui/button";
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
  const qc = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const accept = useCallback((f: File) => {
    setError(null);
    if (!_ALLOWED.includes(f.type)) {
      setError("Format harus JPEG atau PNG");
      setFile(null);
      setPreview(null);
      return;
    }
    if (f.size > _MAX_BYTES) {
      setError("Berkas melebihi 10 MB");
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
    onDropRejected: () => setError("Berkas ditolak: pastikan JPEG/PNG dan maks 10 MB"),
  });

  const mutation = useMutation({
    mutationFn: () => {
      if (!file) throw new Error("Tidak ada berkas");
      return uploadEcgStudy(encounterId, file);
    },
    onSuccess: () => {
      setFile(null);
      setPreview(null);
      setError(null);
      qc.invalidateQueries({ queryKey: ecgKeys.list(encounterId) });
      onUploadSuccess?.();
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Gagal mengunggah"),
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
          "flex items-center justify-between gap-4 rounded-sm border-2 border-dashed px-4 py-4 transition-colors",
          isDragActive
            ? "border-primary bg-affirmed-soft"
            : "border-border-strong bg-sunken hover:bg-affirmed-soft/50",
        )}
      >
        <div className="flex items-center gap-3">
          <UploadCloud className="h-5 w-5 text-primary shrink-0" aria-hidden="true" />
          <div className="text-sm">
            <span className="font-medium text-foreground">Seret EKG ke sini</span>
            <span className="text-muted-foreground hidden sm:inline"> atau pilih berkas</span>
            <p className="text-xs text-muted-foreground mt-0.5">JPEG/PNG, maks 10 MB</p>
          </div>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="cursor-pointer shrink-0"
          onClick={open}
        >
          <ImageUp className="mr-1.5 h-4 w-4" aria-hidden="true" />
          Pilih berkas
        </Button>
        {/* The label keeps the accessible name "Pilih berkas" for tests + a11y. */}
        <label htmlFor="ecg-file" className="sr-only">
          Pilih berkas EKG
        </label>
        <input id="ecg-file" {...getInputProps()} />
      </div>

      {preview && file && (
        <div className="flex items-center gap-3 rounded-sm border border-border-strong bg-paper p-2">
          <img src={preview} alt="Pratinjau EKG" className="h-12 w-12 rounded-sm object-cover" />
          <div className="flex flex-1 flex-col gap-0.5 text-sm">
            <span className="truncate font-medium text-foreground">{file.name}</span>
            <span className="tabular text-xs text-muted-foreground">
              {formatBytes(file.size)} • {file.type.replace("image/", "").toUpperCase()}
            </span>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-8 w-8 cursor-pointer shrink-0"
            onClick={clearFile}
            aria-label="Hapus berkas terpilih"
          >
            <X className="h-4 w-4" />
          </Button>
          <Button
            disabled={!file || mutation.isPending}
            onClick={() => mutation.mutate()}
            className="cursor-pointer shrink-0"
            size="sm"
          >
            {mutation.isPending ? "Mengunggah..." : "Unggah"}
          </Button>
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
