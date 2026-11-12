"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from "react";
import { authService, UserAccount } from "@/services/authService";

const TOKEN_KEY = "autotutor_auth_token";
const USER_KEY = "autotutor_auth_user";

export interface AuthContextType {
  user: UserAccount | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<{ token: string; user: UserAccount }>;
  register: (data: {
    username: string;
    name: string;
    password: string;
    role?: "student" | "teacher";
  }) => Promise<{ token: string; user: UserAccount }>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserAccount | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Restore session once on root mount
  useEffect(() => {
    try {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);

      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));

        authService
          .me(storedToken)
          .then((res) => {
            if (res.authenticated && res.user) {
              setUser(res.user);
              localStorage.setItem(USER_KEY, JSON.stringify(res.user));
            } else {
              localStorage.removeItem(TOKEN_KEY);
              localStorage.removeItem(USER_KEY);
              setToken(null);
              setUser(null);
            }
          })
          .catch(() => {
            // Keep offline session
          });
      }
    } catch (e) {
      console.warn("Falha ao restaurar autenticação:", e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await authService.login({ username, password });
      setToken(res.token);
      setUser(res.user);
      localStorage.setItem(TOKEN_KEY, res.token);
      localStorage.setItem(USER_KEY, JSON.stringify(res.user));
      document.cookie = `autotutor_token=${res.token}; path=/; max-age=86400; SameSite=Lax`;
      return res;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(
    async (data: {
      username: string;
      name: string;
      password: string;
      role?: "student" | "teacher";
    }) => {
      setIsLoading(true);
      try {
        const res = await authService.register(data);
        setToken(res.token);
        setUser(res.user);
        localStorage.setItem(TOKEN_KEY, res.token);
        localStorage.setItem(USER_KEY, JSON.stringify(res.user));
        document.cookie = `autotutor_token=${res.token}; path=/; max-age=86400; SameSite=Lax`;
        return res;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const logout = useCallback(async () => {
    if (token) {
      await authService.logout(token).catch(console.warn);
    }
    setToken(null);
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    document.cookie = "autotutor_token=; path=/; max-age=0";
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  }, [token]);

  const value = useMemo<AuthContextType>(
    () => ({
      user,
      token,
      isLoading,
      isAuthenticated: !!user,
      login,
      register,
      logout,
    }),
    [user, token, isLoading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

const DEFAULT_AUTH_FALLBACK: AuthContextType = {
  user: null,
  token: null,
  isLoading: false,
  isAuthenticated: false,
  login: async () => {
    throw new Error("AuthProvider ausente.");
  },
  register: async () => {
    throw new Error("AuthProvider ausente.");
  },
  logout: async () => {},
};

export function useAuthContext(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    if (process.env.NODE_ENV !== "production") {
      console.warn("useAuthContext chamado fora de um AuthProvider. Fornecendo estado desautenticado seguro.");
    }
    return DEFAULT_AUTH_FALLBACK;
  }
  return context;
}
