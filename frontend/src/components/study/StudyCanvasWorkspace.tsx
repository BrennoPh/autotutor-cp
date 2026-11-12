"use client";

import React, { useState } from "react";
import { MarkdownViewer } from "@/components/common/MarkdownViewer";
import { GraphLabWorkspace } from "@/components/whiteboard/GraphLabWorkspace";
import { GraphNode, GraphEdge } from "@/types/graphLab";
import {
  BookOpen,
  LayoutGrid,
  Maximize2,
  Network,
  Layers,
  ArrowRight,
  Code2,
} from "lucide-react";

interface StudyCanvasWorkspaceProps {
  markdown: string;
  title: string;
  whiteboardPreset?: {
    topic: string;
    algorithm: "dfs" | "bfs" | "custom_cpp";
    nodes: Array<{ id: string; label: string; x?: number; y?: number }>;
    edges: Array<{ id: string; from: string; to: string; directed: boolean }>;
  };
}

export function StudyCanvasWorkspace({
  markdown,
  title,
  whiteboardPreset,
}: StudyCanvasWorkspaceProps) {
  const [viewMode, setViewMode] = useState<"split" | "reader" | "canvas">("split");
  const [projectedPreset, setProjectedPreset] = useState<typeof whiteboardPreset | null>(
    whiteboardPreset || null
  );

  const handleProjectToWhiteboard = () => {
    if (whiteboardPreset) {
      setProjectedPreset({ ...whiteboardPreset });
      if (viewMode === "reader") {
        setViewMode("split");
      }
    }
  };

  const initialNodes: GraphNode[] | undefined = projectedPreset?.nodes?.map((n, idx) => ({
    id: n.id,
    label: n.label || n.id,
    x: n.x ?? (120 + (idx % 3) * 140),
    y: n.y ?? (100 + Math.floor(idx / 3) * 120),
    state: "unvisited",
  }));

  const initialEdges: GraphEdge[] | undefined = projectedPreset?.edges?.map((e, idx) => ({
    id: `edge_${idx}`,
    from: e.from,
    to: e.to,
    directed: e.directed ?? true,
    state: "normal",
  }));

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] rounded-2xl border border-border bg-card/60 backdrop-blur-xl overflow-hidden shadow-2xl">
      {/* Top Controller Bar */}
      <div className="h-12 px-4 border-b border-border bg-slate-900/60 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-primary" />
          <span className="text-xs font-semibold text-foreground truncate max-w-xs">{title}</span>
        </div>

        {/* Action Controls & Mode Switcher */}
        <div className="flex items-center gap-2">
          {whiteboardPreset && (
            <button
              onClick={handleProjectToWhiteboard}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-200 border border-slate-700/60 hover:bg-slate-700 transition-colors shadow-sm"
              title="Carrega os nós e arestas deste estudo no Quadro Branco"
            >
              <Network className="w-3.5 h-3.5 text-blue-400" />
              <span>Projetar no Quadro</span>
            </button>
          )}

          <div className="flex items-center bg-secondary/80 p-0.5 rounded-lg border border-border text-xs">
            <button
              onClick={() => setViewMode("reader")}
              className={`px-2.5 py-1 rounded-md transition-all ${
                viewMode === "reader" ? "bg-primary text-primary-foreground font-semibold shadow-sm" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <BookOpen className="w-3.5 h-3.5 inline mr-1" />
              <span>Texto</span>
            </button>
            <button
              onClick={() => setViewMode("split")}
              className={`px-2.5 py-1 rounded-md transition-all ${
                viewMode === "split" ? "bg-primary text-primary-foreground font-semibold shadow-sm" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <LayoutGrid className="w-3.5 h-3.5 inline mr-1" />
              <span>Obsidian Canvas</span>
            </button>
            <button
              onClick={() => setViewMode("canvas")}
              className={`px-2.5 py-1 rounded-md transition-all ${
                viewMode === "canvas" ? "bg-primary text-primary-foreground font-semibold shadow-sm" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Code2 className="w-3.5 h-3.5 inline mr-1" />
              <span>Quadro</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Workspace Body */}
      <div className="flex-1 flex flex-col lg:flex-row min-h-0 overflow-hidden">
        {/* Left Pane: Markdown Document */}
        {(viewMode === "split" || viewMode === "reader") && (
          <div
            className={`overflow-y-auto p-6 ${
              viewMode === "split" ? "w-full lg:w-1/2 border-b lg:border-b-0 lg:border-r border-border" : "w-full"
            }`}
          >
            <MarkdownViewer content={markdown} />
          </div>
        )}

        {/* Right Pane: Interactive Whiteboard Lab */}
        {(viewMode === "split" || viewMode === "canvas") && (
          <div className={`flex flex-col min-h-0 overflow-hidden ${viewMode === "split" ? "w-full lg:w-1/2" : "w-full"}`}>
            <GraphLabWorkspace
              compact={viewMode === "split"}
              initialNodes={initialNodes}
              initialEdges={initialEdges}
              initialAlgorithm={projectedPreset?.algorithm === "bfs" ? "bfs" : "dfs"}
            />
          </div>
        )}
      </div>
    </div>
  );
}
