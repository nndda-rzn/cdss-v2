import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api/client";
import { cn } from "@/lib/utils";

interface AuthedImageProps {
  /** Server path under /uploads (e.g. "uploads/ecg/1/1/ECG-P1-x.jpg"). */
  path: string;
  alt: string;
  className?: string;
}

/**
 * Renders an image from a JWT-protected endpoint. A plain <img src> cannot
 * attach the bearer token, so we fetch the bytes via apiFetch (which adds the
 * Authorization header + refresh handling) and render an object URL.
 */
export function AuthedImage({ path, alt, className }: AuthedImageProps) {
  const [src, setSrc] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let revoked = false;
    let objectUrl: string | null = null;
    setFailed(false);
    setSrc(null);

    const href = path.startsWith("/") ? path : `/${path}`;
    apiFetch(href)
      .then(async (resp) => {
        if (!resp.ok) throw new Error(String(resp.status));
        const blob = await resp.blob();
        if (revoked) return;
        objectUrl = URL.createObjectURL(blob);
        setSrc(objectUrl);
      })
      .catch(() => !revoked && setFailed(true));

    return () => {
      revoked = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [path]);

  if (failed) {
    return (
      <div
        className={cn(
          "flex items-center justify-center bg-charcoal-50 text-xs text-muted-foreground",
          className,
        )}
      >
        Gambar tidak tersedia
      </div>
    );
  }

  if (!src) {
    return <div className={cn("animate-pulse bg-charcoal-100", className)} aria-hidden="true" />;
  }

  return <img src={src} alt={alt} className={className} loading="lazy" />;
}

AuthedImage.displayName = "AuthedImage";
