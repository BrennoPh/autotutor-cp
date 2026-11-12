import { apiRequest } from "./apiClient";

export interface ProblemSummary {
  id: string;
  title: string;
  topic: string;
  difficulty: "Iniciante" | "Intermediário" | "Avançado";
  tags: string[];
  time_limit_sec: number;
  memory_limit_mb: number;
  complexity: string;
  approach_summary: string;
}

export interface ProblemDetail extends ProblemSummary {
  family?: string;
  math_essence: string;
  core_concepts: string[];
  statement: string;
  constraints: Record<string, any>;
  examples: Array<{
    input: string;
    output: string;
    explanation?: string;
  }>;
  starter_code: {
    cpp: string;
    python: string;
  };
}

export const problemService = {
  async listProblems(params?: {
    topic?: string;
    difficulty?: string;
    search?: string;
  }): Promise<{ total: number; problems: ProblemSummary[] }> {
    const query = new URLSearchParams();
    if (params?.topic) query.set("topic", params.topic);
    if (params?.difficulty) query.set("difficulty", params.difficulty);
    if (params?.search) query.set("search", params.search);

    const qs = query.toString();
    return apiRequest<{ total: number; problems: ProblemSummary[] }>(
      `/api/problems${qs ? `?${qs}` : ""}`
    );
  },

  async getProblem(id: string): Promise<ProblemDetail> {
    return apiRequest<ProblemDetail>(`/api/problems/${id}`);
  },
};
