import React, { useRef, useEffect, useState, useCallback } from "react";
import { GraphNode, GraphEdge, NodeVisualState, EdgeVisualState } from "@/types/graphLab";
import { Focus } from "lucide-react";

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  nodeStates?: Record<string, NodeVisualState>;
  edgeStates?: Record<string, EdgeVisualState>;
  activeNodeId?: string | null;
  activeEdgeId?: string | null;
  mode: "select" | "connect" | "add_node";
  onNodesChange: (nodes: GraphNode[]) => void;
  onEdgesChange: (edges: GraphEdge[]) => void;
}

const NODE_RADIUS = 24;

function fitNodesToCanvas(
  nodes: GraphNode[],
  width: number,
  height: number,
  padding = 60
): GraphNode[] {
  if (!nodes || nodes.length === 0) return nodes;

  let minX = Infinity, maxX = -Infinity;
  let minY = Infinity, maxY = -Infinity;

  nodes.forEach((n) => {
    minX = Math.min(minX, n.x);
    maxX = Math.max(maxX, n.x);
    minY = Math.min(minY, n.y);
    maxY = Math.max(maxY, n.y);
  });

  const currentW = Math.max(maxX - minX, 1);
  const currentH = Math.max(maxY - minY, 1);

  const availW = Math.max(width - padding * 2, 120);
  const availH = Math.max(height - padding * 2, 120);

  const scale = Math.min(availW / currentW, availH / currentH, 1.0);

  const targetCenterX = width / 2;
  const targetCenterY = height / 2;
  const currentCenterX = (minX + maxX) / 2;
  const currentCenterY = (minY + maxY) / 2;

  return nodes.map((n) => {
    const relX = n.x - currentCenterX;
    const relY = n.y - currentCenterY;
    const scaledX = targetCenterX + relX * scale;
    const scaledY = targetCenterY + relY * scale;

    const clampedX = Math.max(padding, Math.min(width - padding, scaledX));
    const clampedY = Math.max(padding, Math.min(height - padding, scaledY));

    return {
      ...n,
      x: Math.round(clampedX),
      y: Math.round(clampedY),
    };
  });
}

export function GraphCanvas({
  nodes,
  edges,
  nodeStates = {},
  edgeStates = {},
  activeNodeId = null,
  activeEdgeId = null,
  mode,
  onNodesChange,
  onEdgesChange,
}: GraphCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Dragging node state
  const [draggedNodeId, setDraggedNodeId] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Elastic edge connection state
  const [connectStartNodeId, setConnectStartNodeId] = useState<string | null>(null);
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number } | null>(null);

  // Helper to find node by coordinates
  const getNodeAt = useCallback(
    (x: number, y: number): GraphNode | undefined => {
      return nodes.find((n) => {
        const dx = n.x - x;
        const dy = n.y - y;
        return Math.sqrt(dx * dx + dy * dy) <= NODE_RADIUS;
      });
    },
    [nodes]
  );

  // High-DPI Render loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const width = canvas.parentElement?.clientWidth || 800;
    const height = canvas.parentElement?.clientHeight || 550;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    ctx.save();
    ctx.scale(dpr, dpr);

    // 1. Background & Grid Dots
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(0, 0, width, height);

    ctx.fillStyle = "#1e293b";
    const dotGap = 28;
    for (let x = 0; x < width; x += dotGap) {
      for (let y = 0; y < height; y += dotGap) {
        ctx.beginPath();
        ctx.arc(x, y, 1.2, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // 2. Draw Edges
    edges.forEach((edge) => {
      const fromNode = nodes.find((n) => n.id === edge.from);
      const toNode = nodes.find((n) => n.id === edge.to);
      if (!fromNode || !toNode) return;

      const currentState = edgeStates[edge.id] || edge.state;
      const isActive = activeEdgeId === edge.id;

      ctx.save();
      ctx.beginPath();

      if (currentState === "back_edge") {
        ctx.setLineDash([6, 4]);
        ctx.strokeStyle = "#ef4444";
        ctx.lineWidth = 3;
      } else if (currentState === "traversed" || isActive) {
        ctx.strokeStyle = "#38bdf8";
        ctx.lineWidth = 3.5;
        ctx.shadowColor = "#38bdf8";
        ctx.shadowBlur = 10;
      } else {
        ctx.strokeStyle = "#475569";
        ctx.lineWidth = 2;
      }

      ctx.moveTo(fromNode.x, fromNode.y);
      ctx.lineTo(toNode.x, toNode.y);
      ctx.stroke();

      // Arrow head for directed edges
      if (edge.directed) {
        const angle = Math.atan2(toNode.y - fromNode.y, toNode.x - fromNode.x);
        const arrowDist = NODE_RADIUS + 4;
        const targetX = toNode.x - Math.cos(angle) * arrowDist;
        const targetY = toNode.y - Math.sin(angle) * arrowDist;

        ctx.fillStyle = ctx.strokeStyle;
        ctx.beginPath();
        ctx.moveTo(targetX, targetY);
        ctx.lineTo(
          targetX - 10 * Math.cos(angle - Math.PI / 6),
          targetY - 10 * Math.sin(angle - Math.PI / 6)
        );
        ctx.lineTo(
          targetX - 10 * Math.cos(angle + Math.PI / 6),
          targetY - 10 * Math.sin(angle + Math.PI / 6)
        );
        ctx.closePath();
        ctx.fill();
      }
      ctx.restore();
    });

    // 3. Draw Elastic Connection Line (Preview)
    if (connectStartNodeId && cursorPos) {
      const startNode = nodes.find((n) => n.id === connectStartNodeId);
      if (startNode) {
        ctx.save();
        ctx.beginPath();
        ctx.strokeStyle = "#38bdf8";
        ctx.lineWidth = 2.5;
        ctx.setLineDash([4, 4]);
        ctx.moveTo(startNode.x, startNode.y);
        ctx.lineTo(cursorPos.x, cursorPos.y);
        ctx.stroke();
        ctx.restore();
      }
    }

    // 4. Draw Nodes
    nodes.forEach((node) => {
      const state = nodeStates[node.id] || node.state;
      const isActive = activeNodeId === node.id;

      let fill = "#4f46e5";
      let stroke = "#818cf8";

      if (state === "visiting") {
        fill = "#f59e0b";
        stroke = "#fbbf24";
      } else if (state === "visited") {
        fill = "#10b981";
        stroke = "#34d399";
      } else if (state === "backtracked") {
        fill = "#64748b";
        stroke = "#94a3b8";
      }

      ctx.save();
      ctx.beginPath();
      ctx.arc(node.x, node.y, NODE_RADIUS, 0, Math.PI * 2);
      ctx.fillStyle = fill;
      ctx.fill();

      ctx.lineWidth = isActive ? 4 : 2.5;
      ctx.strokeStyle = isActive ? "#ffffff" : stroke;
      if (isActive) {
        ctx.shadowColor = fill;
        ctx.shadowBlur = 16;
      }
      ctx.stroke();

      // Node Label
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 13px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(node.label, node.x, node.y);
      ctx.restore();
    });

    ctx.restore();
  }, [nodes, edges, nodeStates, edgeStates, activeNodeId, activeEdgeId, connectStartNodeId, cursorPos]);

  // Pointer Handlers
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const clickedNode = getNodeAt(x, y);

    if (mode === "connect") {
      if (clickedNode) {
        setConnectStartNodeId(clickedNode.id);
        setCursorPos({ x, y });
      }
    } else if (mode === "select") {
      if (clickedNode) {
        setDraggedNodeId(clickedNode.id);
        setDragOffset({ x: x - clickedNode.x, y: y - clickedNode.y });
      }
    } else if (mode === "add_node" && !clickedNode) {
      const nextId = String(nodes.length + 1);
      const newNode: GraphNode = {
        id: nextId,
        x,
        y,
        label: nextId,
        state: "unvisited",
      };
      onNodesChange([...nodes, newNode]);
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (mode === "connect" && connectStartNodeId) {
      setCursorPos({ x, y });
    } else if (mode === "select" && draggedNodeId) {
      onNodesChange(
        nodes.map((n) => (n.id === draggedNodeId ? { ...n, x: x - dragOffset.x, y: y - dragOffset.y } : n))
      );
    }
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (mode === "connect" && connectStartNodeId) {
      const rect = e.currentTarget.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const targetNode = getNodeAt(x, y);

      if (targetNode && targetNode.id !== connectStartNodeId) {
        const newEdge: GraphEdge = {
          id: `e-${connectStartNodeId}-${targetNode.id}`,
          from: connectStartNodeId,
          to: targetNode.id,
          directed: true,
          state: "normal",
        };
        // Avoid duplicate edges
        if (!edges.some((e) => e.from === newEdge.from && e.to === newEdge.to)) {
          onEdgesChange([...edges, newEdge]);
        }
      }
      setConnectStartNodeId(null);
      setCursorPos(null);
    } else if (mode === "select") {
      setDraggedNodeId(null);
    }
  };

  // Auto-fit whenever node count changes if any node is out of viewport
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || nodes.length === 0) return;
    const width = canvas.parentElement?.clientWidth || 800;
    const height = canvas.parentElement?.clientHeight || 550;
    const isOutOfBounds = nodes.some(
      (n) => n.x < 40 || n.x > width - 40 || n.y < 40 || n.y > height - 40
    );
    if (isOutOfBounds) {
      const adjusted = fitNodesToCanvas(nodes, width, height);
      onNodesChange(adjusted);
    }
  }, [nodes.length]);

  const handleAutoFit = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const width = canvas.parentElement?.clientWidth || 800;
    const height = canvas.parentElement?.clientHeight || 550;
    const adjusted = fitNodesToCanvas(nodes, width, height);
    onNodesChange(adjusted);
  };

  return (
    <div className="relative w-full h-full min-h-[480px] rounded-2xl overflow-hidden border border-border bg-[#0f172a] shadow-inner select-none">
      <canvas
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        className="cursor-crosshair w-full h-full"
      />

      {/* Floating Auto-Fit Button */}
      <button
        type="button"
        onClick={handleAutoFit}
        className="absolute bottom-3 right-3 flex items-center gap-1.5 px-3 py-1.5 bg-slate-900/90 hover:bg-slate-800 text-slate-200 hover:text-white rounded-xl text-xs font-semibold border border-slate-700 shadow-lg backdrop-blur-md transition-all active:scale-95"
        title="Centralizar e ajustar nós dentro do campo de visão"
      >
        <Focus className="w-3.5 h-3.5 text-sky-400" />
        <span>Centralizar Grafo</span>
      </button>
    </div>
  );
}
