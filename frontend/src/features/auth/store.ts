import { create } from "zustand";

import {
  clearTokens,
  loadTokens,
  saveTokens,
  loadRememberMe,
  saveRememberMe,
} from "@/lib/api/auth-token";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  rememberMe: boolean;
  setTokens: (access: string, refresh: string) => void;
  setRememberMe: (value: boolean) => void;
  clear: () => void;
}

const initial = loadTokens();

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: initial.accessToken,
  refreshToken: initial.refreshToken,
  rememberMe: loadRememberMe(),
  setTokens: (access, refresh) => {
    saveTokens(access, refresh);
    set({ accessToken: access, refreshToken: refresh });
  },
  setRememberMe: (value) => {
    saveRememberMe(value);
    set({ rememberMe: value });
  },
  clear: () => {
    clearTokens();
    set({ accessToken: null, refreshToken: null });
  },
}));
