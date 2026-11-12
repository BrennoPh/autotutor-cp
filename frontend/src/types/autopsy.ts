export type AutopsyEventClass =
  | "init"
  | "dequeue"
  | "visit_edge"
  | "cross_edge"
  | "enter_dfs"
  | "leave_dfs"
  | "back_edge_cycle"
  | "death_point"
  | "default";

export interface AutopsyTimelineStep {
  step: number;
  event: string;
  active_node: string | null;
  active_edge: { from: string; to: string } | null;
  variables: Record<string, string | number | boolean>;
  visited: string[];
  explanation: string;
}

export interface AutopsyResult {
  status: "success" | "tle" | "error";
  total_steps: number;
  failure_step: number | null;
  failure_reason: string | null;
  timeline: AutopsyTimelineStep[];
  cpp_validation?: { valid: boolean; message: string };
  message?: string;
}
