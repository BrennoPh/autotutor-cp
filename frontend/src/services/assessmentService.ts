import { apiRequest } from "./apiClient";

export interface DiagnosticQuestion {
  id: string;
  topic: string;
  prompt: string;
  options: string[];
}

export interface AssessmentSubmission {
  target_goal: string;
  hours_per_day: number;
  language: string;
  answers: Record<string, string | number>;
}

export interface AssessmentResult {
  score: number;
  level: "Iniciante" | "Intermediário" | "Avançado";
  correct_count: number;
  total_questions: number;
  strong_topics: string[];
  gap_topics: string[];
}

export const assessmentService = {
  async getQuiz(): Promise<{ total: number; questions: DiagnosticQuestion[] }> {
    return apiRequest<{ total: number; questions: DiagnosticQuestion[] }>(
      "/api/assessment/onboarding"
    );
  },

  async submitAssessment(payload: AssessmentSubmission): Promise<AssessmentResult> {
    return apiRequest<AssessmentResult>("/api/assessment/submit", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
