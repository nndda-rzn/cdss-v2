import { create } from "zustand";

import { clearTokens, loadTokens, saveTokens } from "@/lib/api/auth-token";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  setTokens: (access: string, refresh: string) => void;
  clear: () => void;
}

const initial = loadTokens();

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: initial.accessToken,
  refreshToken: initial.refreshToken,
  setTokens: (access, refresh) => {
    saveTokens(access, refresh);
    set({ accessToken: access, refreshToken: refresh });
  },
  clear: () => {
    clearTokens();
    set({ accessToken: null, refreshToken: null });
  },
}));
