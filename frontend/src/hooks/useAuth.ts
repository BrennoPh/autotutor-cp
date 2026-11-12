"use client";

import { useAuthContext } from "@/context/AuthContext";

/**
 * Hook de autenticação global.
 * Consome o singleton AuthContext para evitar checagens e requisições repetidas a cada troca de rota.
 */
export function useAuth() {
  return useAuthContext();
}
