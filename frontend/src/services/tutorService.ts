import { apiRequest } from "./apiClient";
import {
  GraduatedHintPayload,
  GraduatedHintResponse,
  PreFlightPayload,
  PreFlightResponse,
} from "@/types/tutor";

export interface TutorChatPayload {
  message: string;
  action?: "hint" | "diagnose" | "explain" | "simplify" | "material" | "problem" | "whiteboard" | "auto";
  problem_id?: string;
  code?: string;
  judge_result?: any;
  collaborative?: boolean;
  student_id?: string;
  thread_id?: string;
}

export interface TutorChatResponse {
  reply: string;
  action: string;
  provider: string;
  collaborative?: boolean;
  agent_trail?: string[];
  diagnostic_output?: {
    verdict?: string;
    diagnosis?: string;
    topic?: string;
  };
  material_output?: {
    title?: string;
    body?: string;
    topic?: string;
  };
  problem_output?: {
    id?: string;
    title?: string;
    statement?: string;
    topic?: string;
    difficulty?: string;
  };
  whiteboard_output?: {
    analysis?: string;
  };
  recalled_memory?: {
    memory_policy?: string;
    recalled_pages?: Array<{ title: string; excerpt: string }>;
  };
  thread_id?: string;
}

export const tutorService = {
  async sendMessage(payload: TutorChatPayload): Promise<TutorChatResponse> {
    return apiRequest<TutorChatResponse>("/api/tutor/chat", {
      method: "POST",
      body: JSON.stringify({ ...payload, collaborative: payload.collaborative ?? true }),
    });
  },

  async sendCollaborativeMessage(payload: TutorChatPayload): Promise<TutorChatResponse> {
    return apiRequest<TutorChatResponse>("/api/agents/collaborative-chat", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getGraduatedHint(payload: GraduatedHintPayload): Promise<GraduatedHintResponse> {
    return apiRequest<GraduatedHintResponse>("/api/tutor/hints", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async evaluatePreflight(payload: PreFlightPayload): Promise<PreFlightResponse> {
    return apiRequest<PreFlightResponse>("/api/tutor/preflight", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
