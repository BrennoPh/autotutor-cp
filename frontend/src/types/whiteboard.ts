export type WhiteboardTool =
  | "pen"
  | "eraser"
  | "node"
  | "arrow"
  | "line"
  | "rect"
  | "select";

export type StickyColor = "yellow" | "cyan" | "green" | "pink" | "orange";

export interface StickyNote {
  id: string;
  x: number;
  y: number;
  text: string;
  color: StickyColor;
  width?: number;
  height?: number;
}

export interface WhiteboardPoint {
  x: number;
  y: number;
}

export interface WhiteboardShape {
  id: string;
  type: "path" | "node" | "arrow" | "line" | "rect";
  points?: WhiteboardPoint[];
  x?: number;
  y?: number;
  x1?: number;
  y1?: number;
  x2?: number;
  y2?: number;
  width?: number;
  height?: number;
  label?: string;
  color: string;
  lineWidth: number;
}

export type DataStructureTab = "stack" | "queue" | "vector";

export interface StackElement {
  id: string;
  value: string;
}

export interface QueueElement {
  id: string;
  value: string;
}

export interface VectorElement {
  id: string;
  value: string;
}
