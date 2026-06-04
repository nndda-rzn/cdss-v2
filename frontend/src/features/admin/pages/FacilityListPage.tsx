import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { adminKeys, fetchFacilities, createFacility, updateFacility } from "../api";
import { FacilityFormModal } from "../components/FacilityFormModal";
import type { AdminFacility } from "../types";

export function FacilityListPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: adminKeys.facilities,
    queryFn: fetchFacilities,
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<AdminFacility | null>(null);

  const createMut = useMutation({
    mutationFn: createFacility,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: adminKeys.facilities });
      setModalOpen(false);
    },
  });

  const updateMut = useMutation({
    mutationFn: ({ id, ...rest }: { id: number } & Record<string, unknown>) =>
      updateFacility(id, rest),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: adminKeys.facilities });
      setModalOpen(false);
      setEditing(null);
    },
  });

  if (isLoading)
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Fasilitas</h1>
        <Button
          onClick={() => {
            setEditing(null);
            setModalOpen(true);
          }}
        >
          <Plus className="mr-1 h-4 w-4" /> Tambah Fasilitas
        </Button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm" aria-label="Daftar Fasilitas Kesehatan">
          <caption className="sr-only">Daftar fasilitas kesehatan yang terintegrasi</caption>
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4">Nama</th>
              <th className="pb-2 pr-4">Kode</th>
              <th className="pb-2 pr-4">Tipe</th>
              <th className="pb-2 pr-4">Status</th>
              <th className="pb-2">Aksi</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((f) => (
              <tr key={f.id} className="border-b">
                <td className="py-2 pr-4">{f.name}</td>
                <td className="py-2 pr-4">{f.code}</td>
                <td className="py-2 pr-4">{f.facility_type}</td>
                <td className="py-2 pr-4">{f.is_active ? "Aktif" : "Nonaktif"}</td>
                <td className="py-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setEditing(f);
                      setModalOpen(true);
                    }}
                    aria-label="Edit fasilitas"
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <FacilityFormModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditing(null);
        }}
        onSave={(d) =>
          editing
            ? updateMut.mutate({ id: editing.id, ...d })
            : createMut.mutate(d as Parameters<typeof createFacility>[0])
        }
        facility={editing}
      />
    </div>
  );
}
