/**
 * Base HTTP client for AutoTutor CP API Gateway.
 * Supports relative Next.js proxy routing (/api/...) and direct backend fallback.
 */

const API_BASE_URL =
  typeof window !== "undefined" && typeof window.document !== "undefined"
    ? "" // Browser environment: Next.js rewrite handles /api -> http://127.0.0.1:8000
    : process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && options.body && typeof options.body === "string") {
    headers.set("Content-Type", "application/json");
  }

  // Automatic Bearer Token injection for session isolation
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("autotutor_auth_token");
    if (token && !headers.has("Authorization")) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (!res.ok) {
      let errorData: any;
      try {
        errorData = await res.json();
      } catch {
        errorData = { message: res.statusText };
      }

      let errorMsg = errorData.error || errorData.message || `Erro na requisição (${res.status})`;
      if (res.status === 500 && (errorMsg === "Internal Server Error" || errorMsg.includes("socket hang up"))) {
        errorMsg = "O servidor do AutoTutor reiniciou ou está temporariamente indisponível. Tente novamente em instantes.";
      }

      throw new ApiError(
        errorMsg,
        res.status,
        errorData
      );
    }

    return (await res.json()) as T;
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    const msg = err.message || "";
    if (msg.includes("Failed to fetch") || msg.includes("NetworkError") || msg.includes("ECONNREFUSED")) {
      throw new ApiError("Não foi possível conectar ao servidor backend (porta 8000). Verifique se o serviço está ativo.", 503);
    }
    throw new ApiError(msg || "Falha de conexão com o servidor AutoTutor.", 500);
  }
}
