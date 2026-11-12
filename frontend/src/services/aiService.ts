import { apiRequest } from "./apiClient";

export interface GenerateMaterialPayload {
  kind: "Conceitual" | "Prático" | "Aprofundamento";
  concept: string;
  level: "Iniciante" | "Intermediário" | "Avançado";
  theme?: string;
  learning_request?: string;
  length?: "Curto" | "Médio" | "Longo";
  depth?: "Visão geral" | "Passo a passo" | "Aprofundada";
  include_examples?: boolean;
  include_exercises?: boolean;
}

export interface GeneratedMaterialResponse {
  title: string;
  markdown: string;
  concept: string;
  level: string;
  artifact_id: string | null;
  sources: Array<{ title: string; url: string; publisher: string }>;
  whiteboard_preset?: {
    topic: string;
    algorithm: "dfs" | "bfs" | "custom_cpp";
    title?: string;
    description?: string;
    nodes: Array<{ id: string; label: string; x?: number; y?: number }>;
    edges: Array<{ id: string; from: string; to: string; directed: boolean }>;
  };
}

export interface GenerateProblemPayload {
  level: "Iniciante" | "Intermediário" | "Avançado";
  concept: string;
  theme?: string;
  learning_request?: string;
}

export interface GeneratedProblemResponse {
  id: string;
  title: string;
  difficulty: string;
  topic: string;
  statement: string;
  complexity: string;
  starter_code: {
    cpp: string;
    python: string;
  };
  examples: Array<{ input: string; output: string; explanation?: string }>;
  total_tests: number;
  fallback_used?: boolean;
  redirect_url: string;
}

export interface GenerateTrackPayload {
  prompt: string;
  difficulty?: "Iniciante" | "Intermediário" | "Avançado";
  subject?: string;
}

export interface GeneratedTrackResponse {
  title: string;
  subject: string;
  difficulty: "Iniciante" | "Intermediário" | "Avançado";
  description: string;
  modules: Array<{
    title: string;
    description: string;
    estimatedMinutes: number;
    lessons: string[];
  }>;
  fallback_used?: boolean;
}

export const aiService = {
  async generateTrack(payload: GenerateTrackPayload): Promise<GeneratedTrackResponse> {
    return apiRequest<GeneratedTrackResponse>("/api/ai/generate-track", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async generateMaterial(payload: GenerateMaterialPayload): Promise<GeneratedMaterialResponse> {
    return apiRequest<GeneratedMaterialResponse>("/api/ai/generate-material", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async generateProblem(payload: GenerateProblemPayload): Promise<GeneratedProblemResponse> {
    return apiRequest<GeneratedProblemResponse>("/api/ai/generate-problem", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async saveLlmConfig(data: { provider: string; api_key?: string; model?: string }): Promise<any> {
    return apiRequest("/api/config/save-llm", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};
