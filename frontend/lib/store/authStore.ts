'use client';

import { create } from 'zustand';
import { User } from '@/lib/api/types';
import { authApi, AuthTokensResponse } from '@/lib/api/auth';
import { setAccessToken, getAccessToken } from '@/lib/api/client';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  loginSuccess: (data: AuthTokensResponse) => void;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
  initAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  loginSuccess: (data) => {
    setAccessToken(data.access);
    if (typeof window !== 'undefined' && data.refresh) {
      localStorage.setItem('okj_refresh_token', data.refresh);
    }
    if (data.user) {
      set({ user: data.user, isAuthenticated: true, isLoading: false });
    }
  },

  logout: async () => {
    const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('okj_refresh_token') : null;
    await authApi.logout(refreshToken);
    setAccessToken(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('okj_refresh_token');
    }
    set({ user: null, isAuthenticated: false });
  },

  logoutAll: async () => {
    await authApi.logoutAll();
    setAccessToken(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('okj_refresh_token');
    }
    set({ user: null, isAuthenticated: false });
  },

  initAuth: async () => {
    set({ isLoading: true });
    const token = getAccessToken();
    if (!token) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      return;
    }
    try {
      const user = await authApi.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      setAccessToken(null);
      if (typeof window !== 'undefined') {
        localStorage.removeItem('okj_refresh_token');
      }
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
