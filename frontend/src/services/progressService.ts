import { apiRequest } from "./apiClient";

export interface SubmissionHistoryItem {
  problem_id: string;
  problem: string;
  topic: string;
  verdict: string;
  time_ms: number;
  language: string;
  timestamp: number;
}

export interface ProgressData {
  profile_id: string;
  total_submissions: number;
  solved_count: number;
  level: string;
  study_hours: number;
  streak_days: number;
  history: SubmissionHistoryItem[];
  onboarding_completed?: boolean;
  diagnostic_score?: number | null;
  strong_topics?: string[];
  gap_topics?: string[];
  completed_lessons?: string[];
  materials_count?: number;
}

export const progressService = {
  async getProgress(): Promise<ProgressData> {
    return apiRequest<ProgressData>("/api/progress");
  },
};
