import { useQuery } from "@tanstack/react-query";
import { Brain } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { adminKeys, fetchModels } from "../api";
import type { AdminModel } from "../types";

function ModelRow({ m }: { m: AdminModel }) {
  return (
    <tr className="border-b">
      <td className="py-2 pr-4 font-medium">
        <span className="flex items-center gap-2">
          <Brain className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
          {m.model_name}
        </span>
      </td>
      <td className="py-2 pr-4">{m.architecture}</td>
      <td className="py-2 pr-4">{m.model_version}</td>
      <td className="py-2 pr-4">{m.model_size_mb} MB</td>
      <td className="py-2 pr-4">
        {m.input_size}x{m.input_size}
      </td>
      <td className="py-2 pr-4">
        <div className="flex flex-wrap gap-1">
          {m.class_names_json.map((cls) => (
            <Badge key={cls} variant="secondary" className="text-xs">
              {cls}
            </Badge>
          ))}
        </div>
      </td>
      <td className="py-2 pr-4">
        {m.is_active ? (
          <Badge variant="default">Active</Badge>
        ) : (
          <Badge variant="outline">Inactive</Badge>
        )}
      </td>
      <td className="py-2 pr-4 font-mono text-xs text-muted-foreground">{m.model_file_path}</td>
    </tr>
  );
}

export function ModelListPage() {
  const { data, isLoading } = useQuery({
    queryKey: adminKeys.models,
    queryFn: fetchModels,
  });

  if (isLoading)
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    );

  return (
    <div className="space-y-4">
      <header>
        <h1 className="text-xl font-semibold">Model AI</h1>
        <p className="text-sm text-muted-foreground">
          Daftar model yang terdaftar di sistem. Model di-register otomatis dari direktori models/.
        </p>
      </header>
      <div className="overflow-x-auto">
        <table className="w-full text-sm" aria-label="Daftar Model AI">
          <caption className="sr-only">Daftar model AI yang terdaftar di sistem</caption>
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4">Nama</th>
              <th className="pb-2 pr-4">Arsitektur</th>
              <th className="pb-2 pr-4">Versi</th>
              <th className="pb-2 pr-4">Ukuran</th>
              <th className="pb-2 pr-4">Input</th>
              <th className="pb-2 pr-4">Class Names</th>
              <th className="pb-2 pr-4">Status</th>
              <th className="pb-2">File Path</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((m) => (
              <ModelRow key={m.id} m={m} />
            ))}
          </tbody>
        </table>
        {data?.items.length === 0 && (
          <p className="py-8 text-center text-sm text-muted-foreground">
            Belum ada model yang terdaftar.
          </p>
        )}
      </div>
    </div>
  );
}
