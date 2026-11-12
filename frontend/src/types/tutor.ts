export type TutorActionType = 
  | "hint"
  | "scaffolding"
  | "minimal_example"
  | "review_code"
  | "explain_analogy"
  | "make_flashcard"
  | "simplify"
  | "generate_quiz";

export interface RagCitation {
  title: string;
  publisher: string;
  url: string;
}

export interface GraduatedHintPayload {
  problem_id: string;
  student_id?: string;
  current_code?: string;
  tier: number;
  user_query?: string;
}

export interface GraduatedHintResponse {
  problem_id: string;
  tier: number;
  tier_name: string;
  title: string;
  hint_markdown: string;
  rag_citations: RagCitation[];
  memory_trigger?: string;
  memory_adaptation?: string;
  zero_leak_verified: boolean;
  next_tier_available: number | null;
}

export interface PreFlightPayload {
  problem_id: string;
  proposed_complexity: string;
  chosen_structure: string;
  estimated_ops?: number;
}

export interface PreFlightResponse {
  status: "APPROVED" | "WARNING" | "REJECTED";
  verdict_preview: "VIABLE" | "TLE_RISK" | "MLE_RISK";
  feedback: string;
  estimated_operations: number;
  time_limit_sec: number;
  edge_cases_to_watch: string[];
}

export interface TutorMessage {
  id: string;
  sender: "user" | "tutor";
  content: string;
  timestamp: string;
  isStreaming?: boolean;
  actionContext?: {
    actionType: TutorActionType;
    snippet: string;
  };
  agentTrail?: string[];
  diagnosticInfo?: string;
  recalledMemoryTitle?: string;
}

export interface QuickSuggestion {
  id: string;
  label: string;
  prompt: string;
  iconName?: string;
}
