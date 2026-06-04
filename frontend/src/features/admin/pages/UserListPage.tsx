import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, UserX, UserCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { adminKeys, fetchUsers, createUser, updateUser } from "../api";
import { UserFormModal } from "../components/UserFormModal";
import type { AdminUser } from "../types";

export function UserListPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: adminKeys.users,
    queryFn: fetchUsers,
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<AdminUser | null>(null);

  const createMut = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: adminKeys.users });
      setModalOpen(false);
    },
  });

  const updateMut = useMutation({
    mutationFn: ({ id, ...rest }: { id: number } & Record<string, unknown>) => updateUser(id, rest),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: adminKeys.users });
      setModalOpen(false);
      setEditing(null);
    },
  });

  const toggleActive = (u: AdminUser) => {
    updateMut.mutate({ id: u.id, is_active: !u.is_active });
  };

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
        <h1 className="text-xl font-semibold">Users</h1>
        <Button
          onClick={() => {
            setEditing(null);
            setModalOpen(true);
          }}
        >
          <Plus className="mr-1 h-4 w-4" /> Tambah User
        </Button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4">Nama</th>
              <th className="pb-2 pr-4">Email</th>
              <th className="pb-2 pr-4">Role</th>
              <th className="pb-2 pr-4">Status</th>
              <th className="pb-2">Aksi</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((u) => (
              <tr key={u.id} className="border-b">
                <td className="py-2 pr-4">{u.name}</td>
                <td className="py-2 pr-4">{u.email}</td>
                <td className="py-2 pr-4">{u.role}</td>
                <td className="py-2 pr-4">{u.is_active ? "Aktif" : "Nonaktif"}</td>
                <td className="py-2 flex gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setEditing(u);
                      setModalOpen(true);
                    }}
                    aria-label="Edit user"
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleActive(u)}
                    aria-label={u.is_active ? "Nonaktifkan user" : "Aktifkan user"}
                  >
                    {u.is_active ? (
                      <UserX className="h-4 w-4" />
                    ) : (
                      <UserCheck className="h-4 w-4" />
                    )}
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <UserFormModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditing(null);
        }}
        onSave={(d) =>
          editing
            ? updateMut.mutate({ id: editing.id, ...d })
            : createMut.mutate(d as Parameters<typeof createUser>[0])
        }
        user={editing}
      />
    </div>
  );
}
