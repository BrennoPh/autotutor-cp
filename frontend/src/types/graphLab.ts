export type NodeVisualState = "unvisited" | "visiting" | "visited" | "backtracked";

export type EdgeVisualState = "normal" | "traversed" | "back_edge";

export interface GraphNode {
  id: string;
  x: number;
  y: number;
  label: string;
  state: NodeVisualState;
}

export interface GraphEdge {
  id: string;
  from: string;
  to: string;
  weight?: number;
  label?: string;
  directed: boolean;
  state: EdgeVisualState;
}

export interface CallStackFrame {
  functionName: string;
  args: Record<string, string | number>;
  callDepth: number;
  localVars: Record<string, string | number | boolean>;
}

export interface MemorySnapshot {
  visited: Record<string, boolean>;
  stack: CallStackFrame[];
  queue?: string[];
  currentDist?: Record<string, number>;
  localVars?: Record<string, string | number | boolean>;
}

export interface ExecutionStep {
  stepIndex: number;
  lineHighlighted: number; // 1-indexed
  memoryState: MemorySnapshot;
  activeNodeId: string | null;
  activeEdgeId: string | null;
  nodeStates: Record<string, NodeVisualState>;
  edgeStates: Record<string, EdgeVisualState>;
  logMessage: string;
}

export type PlaybackStatus = "idle" | "playing" | "paused" | "completed";

export interface GraphLabModel {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
