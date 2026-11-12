import { apiRequest } from "./apiClient";

export interface UserAccount {
  id: string;
  username: string;
  name: string;
  role: "student" | "teacher";
  profile_id: string;
}

export interface AuthResponse {
  message?: string;
  token: string;
  user: UserAccount;
}

export const authService = {
  async register(data: {
    username: string;
    name: string;
    password: string;
    role?: "student" | "teacher";
  }): Promise<AuthResponse> {
    return apiRequest<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async login(data: { username: string; password: string }): Promise<AuthResponse> {
    return apiRequest<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async me(token: string): Promise<{ authenticated: boolean; user: UserAccount | null }> {
    return apiRequest<{ authenticated: boolean; user: UserAccount | null }>("/api/auth/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  async logout(token: string): Promise<void> {
    try {
      await apiRequest("/api/auth/logout", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch {
      // Ignore
    }
  },
};
