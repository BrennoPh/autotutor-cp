import { apiRequest } from "./apiClient";
import { GraphNode, GraphEdge, ExecutionStep } from "@/types/graphLab";
import { AutopsyResult } from "@/types/autopsy";

export interface PresetItem {
  id: string;
  name: string;
  description: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface SimulationResult {
  tape: ExecutionStep[];
  total_steps: number;
  is_valid_cpp?: boolean;
  compilation_status?: "compiled" | "syntax_error" | "not_code" | "timeout" | "error";
  compiler_message?: string;
  execution_output?: string;
}

export interface WhiteboardPromptResult {
  title?: string;
  topic?: string;
  algorithm: "dfs" | "bfs" | "dijkstra" | "bst";
  nodes: GraphNode[];
  edges: GraphEdge[];
  cpp_code: string;
  explanation: string;
}

export const whiteboardService = {
  async getPresets(): Promise<{ presets: Record<string, any> }> {
    return apiRequest<{ presets: Record<string, any> }>("/api/whiteboard/presets");
  },

  async parseGraph(rawText: string, presetName?: string): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
    return apiRequest<{ nodes: GraphNode[]; edges: GraphEdge[] }>("/api/whiteboard/parse-graph", {
      method: "POST",
      body: JSON.stringify({ raw_text: rawText, preset_name: presetName }),
    });
  },

  async simulateAlgorithm(payload: {
    codeText: string;
    nodes: GraphNode[];
    edges: GraphEdge[];
    startNode?: string;
    maxSteps?: number;
  }): Promise<SimulationResult> {
    return apiRequest<SimulationResult>("/api/whiteboard/simulate", {
      method: "POST",
      body: JSON.stringify({
        code_text: payload.codeText,
        nodes: payload.nodes,
        edges: payload.edges,
        start_node: payload.startNode,
        max_steps: payload.maxSteps ?? 500,
      }),
    });
  },

  async analyzeBoard(nodes: GraphNode[], edges: GraphEdge[]): Promise<any> {
    return apiRequest("/api/whiteboard/analyze", {
      method: "POST",
      body: JSON.stringify({ nodes, edges }),
    });
  },

  async runAutopsy(payload: {
    codeText?: string;
    nodes: GraphNode[];
    edges: GraphEdge[];
    algorithm?: "dfs" | "bfs" | "dijkstra" | "bst";
    startNode?: string;
    maxSteps?: number;
  }): Promise<AutopsyResult> {
    return apiRequest<AutopsyResult>("/api/whiteboard/autopsy", {
      method: "POST",
      body: JSON.stringify({
        code_text: payload.codeText || "",
        nodes: payload.nodes,
        edges: payload.edges,
        algorithm: payload.algorithm || "bfs",
        start_node: payload.startNode,
        max_steps: payload.maxSteps ?? 200,
      }),
    });
  },

  async generateFromPrompt(
    payload: string | { prompt: string; currentNodes?: GraphNode[]; currentEdges?: GraphEdge[] }
  ): Promise<WhiteboardPromptResult> {
    const bodyObj =
      typeof payload === "string"
        ? { prompt: payload, current_nodes: [], current_edges: [] }
        : {
            prompt: payload.prompt,
            current_nodes: payload.currentNodes || [],
            current_edges: payload.currentEdges || [],
          };
    return apiRequest<WhiteboardPromptResult>("/api/whiteboard/prompt", {
      method: "POST",
      body: JSON.stringify(bodyObj),
    });
  },
};
