"use client";

import React, { useRef, useEffect, useState, useCallback } from "react";
import { WhiteboardShape, WhiteboardTool, WhiteboardPoint } from "@/types/whiteboard";

interface FreehandCanvasProps {
  tool: WhiteboardTool;
  color: string;
  lineWidth: number;
  nodeLabel: string;
  shapes: WhiteboardShape[];
  onShapesChange: (shapes: WhiteboardShape[]) => void;
  canvasRef: React.RefObject<HTMLCanvasElement>;
}

export function FreehandCanvas({
  tool,
  color,
  lineWidth,
  nodeLabel,
  shapes,
  onShapesChange,
  canvasRef,
}: FreehandCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const currentShapeRef = useRef<WhiteboardShape | null>(null);

  // Redraw all shapes on canvas
  const redraw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);

    // Draw all committed shapes
    shapes.forEach((shape) => {
      ctx.save();
      ctx.strokeStyle = shape.color;
      ctx.fillStyle = shape.color;
      ctx.lineWidth = shape.lineWidth;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";

      if (shape.type === "path" && shape.points && shape.points.length > 0) {
        ctx.beginPath();
        shape.points.forEach((pt, i) => {
          if (i === 0) ctx.moveTo(pt.x, pt.y);
          else ctx.lineTo(pt.x, pt.y);
        });
        ctx.stroke();
      } else if (shape.type === "node" && shape.x !== undefined && shape.y !== undefined) {
        ctx.fillStyle = "#1e1b4b";
        ctx.strokeStyle = shape.color;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(shape.x, shape.y, 22, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 13px system-ui, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(shape.label || "1", shape.x, shape.y);
      } else if (
        (shape.type === "arrow" || shape.type === "line") &&
        shape.x1 !== undefined &&
        shape.y1 !== undefined &&
        shape.x2 !== undefined &&
        shape.y2 !== undefined
      ) {
        ctx.beginPath();
        ctx.moveTo(shape.x1, shape.y1);
        ctx.lineTo(shape.x2, shape.y2);
        ctx.stroke();

        if (shape.type === "arrow") {
          const angle = Math.atan2(shape.y2 - shape.y1, shape.x2 - shape.x1);
          const headLen = 14;
          ctx.beginPath();
          ctx.moveTo(shape.x2, shape.y2);
          ctx.lineTo(
            shape.x2 - headLen * Math.cos(angle - Math.PI / 6),
            shape.y2 - headLen * Math.sin(angle - Math.PI / 6)
          );
          ctx.lineTo(
            shape.x2 - headLen * Math.cos(angle + Math.PI / 6),
            shape.y2 - headLen * Math.sin(angle + Math.PI / 6)
          );
          ctx.closePath();
          ctx.fill();
        }
      } else if (
        shape.type === "rect" &&
        shape.x !== undefined &&
        shape.y !== undefined &&
        shape.width !== undefined &&
        shape.height !== undefined
      ) {
        ctx.strokeStyle = shape.color;
        ctx.fillStyle = shape.color + "15";
        ctx.strokeRect(shape.x, shape.y, shape.width, shape.height);
        ctx.fillRect(shape.x, shape.y, shape.width, shape.height);
      }

      ctx.restore();
    });

    // Draw active drawing shape in progress
    if (currentShapeRef.current) {
      const active = currentShapeRef.current;
      ctx.save();
      ctx.strokeStyle = active.color;
      ctx.fillStyle = active.color;
      ctx.lineWidth = active.lineWidth;
      ctx.lineCap = "round";

      if (active.type === "path" && active.points && active.points.length > 0) {
        ctx.beginPath();
        active.points.forEach((pt, i) => {
          if (i === 0) ctx.moveTo(pt.x, pt.y);
          else ctx.lineTo(pt.x, pt.y);
        });
        ctx.stroke();
      } else if (active.type === "line" || active.type === "arrow") {
        if (
          active.x1 !== undefined &&
          active.y1 !== undefined &&
          active.x2 !== undefined &&
          active.y2 !== undefined
        ) {
          ctx.beginPath();
          ctx.moveTo(active.x1, active.y1);
          ctx.lineTo(active.x2, active.y2);
          ctx.stroke();
        }
      } else if (active.type === "rect") {
        if (
          active.x !== undefined &&
          active.y !== undefined &&
          active.width !== undefined &&
          active.height !== undefined
        ) {
          ctx.strokeRect(active.x, active.y, active.width, active.height);
        }
      }
      ctx.restore();
    }
  }, [shapes, canvasRef]);

  // Handle Resize and DPR
  const resizeCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;

    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.scale(dpr, dpr);
    }
    redraw();
  }, [canvasRef, redraw]);

  useEffect(() => {
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);
    return () => window.removeEventListener("resize", resizeCanvas);
  }, [resizeCanvas]);

  useEffect(() => {
    redraw();
  }, [shapes, redraw]);

  const getPos = (e: React.PointerEvent<HTMLCanvasElement>): WhiteboardPoint => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
  };

  const handlePointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const pos = getPos(e);

    if (tool === "eraser") {
      // Remove shapes near the click
      const filtered = shapes.filter((s) => {
        if (s.type === "node" && s.x !== undefined && s.y !== undefined) {
          const dist = Math.hypot(s.x - pos.x, s.y - pos.y);
          return dist > 25;
        }
        if (s.type === "path" && s.points) {
          return !s.points.some((p) => Math.hypot(p.x - pos.x, p.y - pos.y) < 18);
        }
        return true;
      });
      onShapesChange(filtered);
      return;
    }

    if (tool === "node") {
      const newNode: WhiteboardShape = {
        id: `node_${Date.now()}`,
        type: "node",
        x: pos.x,
        y: pos.y,
        label: nodeLabel || "1",
        color,
        lineWidth,
      };
      onShapesChange([...shapes, newNode]);
      return;
    }

    setIsDrawing(true);
    (e.target as HTMLElement).setPointerCapture(e.pointerId);

    if (tool === "pen") {
      currentShapeRef.current = {
        id: `path_${Date.now()}`,
        type: "path",
        points: [pos],
        color,
        lineWidth,
      };
    } else if (tool === "arrow" || tool === "line") {
      currentShapeRef.current = {
        id: `line_${Date.now()}`,
        type: tool,
        x1: pos.x,
        y1: pos.y,
        x2: pos.x,
        y2: pos.y,
        color,
        lineWidth,
      };
    } else if (tool === "rect") {
      currentShapeRef.current = {
        id: `rect_${Date.now()}`,
        type: "rect",
        x: pos.x,
        y: pos.y,
        width: 0,
        height: 0,
        color,
        lineWidth,
      };
    }
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !currentShapeRef.current) return;
    const pos = getPos(e);
    const shape = currentShapeRef.current;

    if (shape.type === "path" && shape.points) {
      shape.points.push(pos);
    } else if (shape.type === "arrow" || shape.type === "line") {
      shape.x2 = pos.x;
      shape.y2 = pos.y;
    } else if (shape.type === "rect" && shape.x !== undefined && shape.y !== undefined) {
      shape.width = pos.x - shape.x;
      shape.height = pos.y - shape.y;
    }

    redraw();
  };

  const handlePointerUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    setIsDrawing(false);
    try {
      (e.target as HTMLElement).releasePointerCapture(e.pointerId);
    } catch {
      // Safe ignore
    }

    if (currentShapeRef.current) {
      onShapesChange([...shapes, currentShapeRef.current]);
      currentShapeRef.current = null;
    }
    redraw();
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full min-h-[580px] bg-slate-950/90 rounded-2xl overflow-hidden border border-border shadow-inner cursor-crosshair select-none"
      style={{
        backgroundImage: "radial-gradient(#334155 1.2px, transparent 1.2px)",
        backgroundSize: "24px 24px",
      }}
    >
      <canvas
        ref={canvasRef}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        className="absolute inset-0 w-full h-full touch-none"
      />
    </div>
  );
}
