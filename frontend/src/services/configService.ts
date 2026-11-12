import { apiRequest } from "./apiClient";

export interface LlmConfig {
  provider: string;
  masked_key: string;
  model: string;
  available_providers: string[];
}

export interface PingResponse {
  ok: boolean;
  provider: string;
  status: string;
  message: string;
}

export const configService = {
  async getConfig(): Promise<LlmConfig> {
    return apiRequest<LlmConfig>("/api/config/llm");
  },

  async ping(payload?: { provider?: string; api_key?: string; model?: string }): Promise<PingResponse> {
    return apiRequest<PingResponse>("/api/config/ping", {
      method: "POST",
      body: JSON.stringify(payload || {}),
    });
  },
};
