import { useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { ecgKeys, uploadEcgStudy } from "./api";

const _ALLOWED = ["image/jpeg", "image/png"];

export function EcgUploadForm({
  encounterId,
  onUploadSuccess,
}: {
  encounterId: string;
  onUploadSuccess?: () => void;
}) {
  const qc = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => {
      if (!file) throw new Error("Tidak ada berkas");
      return uploadEcgStudy(encounterId, file);
    },
    onSuccess: () => {
      setFile(null);
      setPreview(null);
      if (inputRef.current) inputRef.current.value = "";
      qc.invalidateQueries({ queryKey: ecgKeys.list(encounterId) });
      onUploadSuccess?.();
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Gagal mengunggah"),
  });

  function onSelect(e: React.ChangeEvent<HTMLInputElement>) {
    setError(null);
    const f = e.target.files?.[0] ?? null;
    if (!f) return;
    if (!_ALLOWED.includes(f.type)) {
      setError("Format harus JPEG atau PNG");
      setFile(null);
      setPreview(null);
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setError("Berkas melebihi 10 MB");
      setFile(null);
      setPreview(null);
      return;
    }
    setFile(f);
    setPreview(URL.createObjectURL(f));
  }

  return (
    <div className="space-y-3">
      <label className="text-sm font-medium" htmlFor="ecg-file">
        Pilih berkas EKG (JPEG/PNG, maks 10 MB)
      </label>
      <input
        id="ecg-file"
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png"
        onChange={onSelect}
        className="block text-sm"
      />
      {preview && <img src={preview} alt="Pratinjau EKG" className="max-h-48 rounded border" />}
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
      <Button disabled={!file || mutation.isPending} onClick={() => mutation.mutate()}>
        {mutation.isPending ? "Mengunggah..." : "Unggah EKG"}
      </Button>
    </div>
  );
}
