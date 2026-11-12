"use client";

import React, { useState, useRef } from "react";
import {
  WhiteboardTool,
  WhiteboardShape,
  StickyNote,
} from "@/types/whiteboard";
import { FreehandCanvas } from "./FreehandCanvas";
import { StickyNotesLayer } from "./StickyNotesLayer";
import { DataStructuresPanel } from "./DataStructuresPanel";
import {
  Pen,
  Circle,
  ArrowRight,
  Minus,
  Square,
  Eraser,
  StickyNote as StickyIcon,
  Undo2,
  Trash2,
  Download,
  Layers,
  Sparkles,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

const PALETTE = [
  { name: "Índigo", color: "#6366f1" },
  { name: "Ciano", color: "#06b6d4" },
  { name: "Verde", color: "#10b981" },
  { name: "Âmbar", color: "#f59e0b" },
  { name: "Vermelho", color: "#ef4444" },
  { name: "Branco", color: "#f8fafc" },
];

export function RealWhiteboardWorkspace() {
  const [tool, setTool] = useState<WhiteboardTool>("pen");
  const [color, setColor] = useState<string>("#6366f1");
  const [lineWidth, setLineWidth] = useState<number>(3);
  const [nodeLabel, setNodeLabel] = useState<string>("1");
  const [shapes, setShapes] = useState<WhiteboardShape[]>([]);
  const [undoHistory, setUndoHistory] = useState<WhiteboardShape[][]>([]);
  const [isDataStructuresOpen, setIsDataStructuresOpen] = useState(true);

  // Sticky Notes State
  const [notes, setNotes] = useState<StickyNote[]>([
    {
      id: "note-1",
      x: 40,
      y: 60,
      text: "Lembrete: Invariante da BFS\nExplora nós por camadas de menor distância usando Fila (FIFO).",
      color: "yellow",
      width: 230,
    },
  ]);

  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleShapesChange = (newShapes: WhiteboardShape[]) => {
    setUndoHistory((prev) => [...prev, shapes]);
    setShapes(newShapes);
  };

  const handleUndo = () => {
    if (undoHistory.length === 0) return;
    const previous = undoHistory[undoHistory.length - 1];
    setShapes(previous);
    setUndoHistory((prev) => prev.slice(0, -1));
  };

  const handleClear = () => {
    if (shapes.length === 0 && notes.length === 0) return;
    setUndoHistory((prev) => [...prev, shapes]);
    setShapes([]);
  };

  const handleAddStickyNote = () => {
    const newNote: StickyNote = {
      id: `note-${Date.now()}`,
      x: 80 + Math.random() * 150,
      y: 80 + Math.random() * 120,
      text: "",
      color: "yellow",
      width: 220,
    };
    setNotes((prev) => [...prev, newNote]);
  };

  const handleUpdateNote = (id: string, updates: Partial<StickyNote>) => {
    setNotes((prev) =>
      prev.map((n) => (n.id === id ? { ...n, ...updates } : n))
    );
  };

  const handleDeleteNote = (id: string) => {
    setNotes((prev) => prev.filter((n) => n.id !== id));
  };

  const handleExportPNG = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const url = canvas.toDataURL("image/png");
    const a = document.createElement("a");
    a.href = url;
    a.download = `quadro-branco-autotutor-${Date.now()}.png`;
    a.click();
  };

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* Real Whiteboard Toolbar */}
      <div className="bg-card/80 backdrop-blur-md border border-border rounded-2xl p-3 flex flex-wrap items-center justify-between gap-3 text-xs select-none shadow-xs">
        {/* Drawing Tools */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            type="button"
            onClick={() => setTool("pen")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-semibold transition-all ${
              tool === "pen"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "bg-secondary/70 text-muted-foreground hover:text-foreground"
            }`}
            title="Caneta livre para anotações e desenhos"
          >
            <Pen className="w-3.5 h-3.5" />
            <span>Caneta</span>
          </button>

          <button
            type="button"
            onClick={() => setTool("eraser")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-semibold transition-all ${
              tool === "eraser"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "bg-secondary/70 text-muted-foreground hover:text-foreground"
            }`}
            title="Borracha para apagar traços e nós"
          >
            <Eraser className="w-3.5 h-3.5" />
            <span>Borracha</span>
          </button>

          <div className="h-5 w-px bg-border/60 mx-1" />

          {/* Node Tool with Label Input */}
          <div className="flex items-center gap-1 bg-secondary/60 p-0.5 rounded-xl border border-border">
            <button
              type="button"
              onClick={() => setTool("node")}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg font-semibold transition-all ${
                tool === "node"
                  ? "bg-primary text-primary-foreground shadow-xs"
                  : "text-muted-foreground hover:text-foreground"
              }`}
              title="Inserir nó de grafo/árvore no clique"
            >
              <Circle className="w-3.5 h-3.5" />
              <span>Nó</span>
            </button>
            <input
              type="text"
              value={nodeLabel}
              onChange={(e) => setNodeLabel(e.target.value)}
              className="w-10 bg-background text-foreground font-mono text-center text-xs py-0.5 rounded border border-border/80 focus:outline-none"
              title="Rótulo do nó"
            />
          </div>

          <button
            type="button"
            onClick={() => setTool("arrow")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-semibold transition-all ${
              tool === "arrow"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "bg-secondary/70 text-muted-foreground hover:text-foreground"
            }`}
            title="Seta direcionada"
          >
            <ArrowRight className="w-3.5 h-3.5" />
            <span>Seta</span>
          </button>

          <button
            type="button"
            onClick={() => setTool("line")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-semibold transition-all ${
              tool === "line"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "bg-secondary/70 text-muted-foreground hover:text-foreground"
            }`}
            title="Linha reta / Aresta"
          >
            <Minus className="w-3.5 h-3.5" />
            <span>Aresta</span>
          </button>

          <button
            type="button"
            onClick={() => setTool("rect")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-semibold transition-all ${
              tool === "rect"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "bg-secondary/70 text-muted-foreground hover:text-foreground"
            }`}
            title="Caixa delimitadora"
          >
            <Square className="w-3.5 h-3.5" />
            <span>Caixa</span>
          </button>

          {/* Add Post-it Action */}
          <button
            type="button"
            onClick={handleAddStickyNote}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/40 font-semibold transition-all"
            title="Adicionar nota adesiva (Post-it) arrastável"
          >
            <StickyIcon className="w-3.5 h-3.5" />
            <span>+ Post-it</span>
          </button>
        </div>

        {/* Colors, Width and Global Actions */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Color Dots */}
          <div className="flex items-center gap-1 bg-secondary/50 p-1 rounded-xl border border-border">
            {PALETTE.map((p) => (
              <button
                key={p.color}
                type="button"
                onClick={() => setColor(p.color)}
                style={{ backgroundColor: p.color }}
                className={`w-5 h-5 rounded-full border-2 transition-transform ${
                  color === p.color
                    ? "border-white scale-110 shadow-xs"
                    : "border-transparent opacity-80 hover:opacity-100"
                }`}
                title={p.name}
              />
            ))}
          </div>

          {/* Stroke Width Selector */}
          <div className="flex items-center gap-1 bg-secondary/50 p-1 rounded-xl border border-border">
            {[2, 4, 8].map((w) => (
              <button
                key={w}
                type="button"
                onClick={() => setLineWidth(w)}
                className={`px-2 py-0.5 rounded text-[10px] font-bold transition-colors ${
                  lineWidth === w
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`}
                title={`Espessura ${w}px`}
              >
                {w === 2 ? "Fina" : w === 4 ? "Média" : "Grossa"}
              </button>
            ))}
          </div>

          <div className="h-5 w-px bg-border/60 mx-1" />

          {/* Undo, Clear & Export */}
          <button
            type="button"
            onClick={handleUndo}
            disabled={undoHistory.length === 0}
            className="p-2 rounded-xl bg-secondary/70 hover:bg-secondary text-muted-foreground hover:text-foreground transition-all disabled:opacity-40"
            title="Desfazer traço (Ctrl+Z)"
          >
            <Undo2 className="w-3.5 h-3.5" />
          </button>

          <button
            type="button"
            onClick={handleClear}
            className="p-2 rounded-xl bg-secondary/70 hover:bg-destructive/20 text-muted-foreground hover:text-destructive transition-all"
            title="Limpar quadro"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>

          <button
            type="button"
            onClick={handleExportPNG}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600/90 hover:bg-emerald-600 text-white font-semibold transition-all shadow-xs"
            title="Exportar lousa em alta resolução (PNG)"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Baixar PNG</span>
          </button>

          {/* Toggle Data Structures Dock */}
          <button
            type="button"
            onClick={() => setIsDataStructuresOpen((prev) => !prev)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-semibold border transition-all ${
              isDataStructuresOpen
                ? "bg-slate-800 text-slate-100 border-slate-700 shadow-xs"
                : "bg-secondary/70 text-muted-foreground hover:text-foreground border-border"
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-primary" />
            <span>Estruturas</span>
            {isDataStructuresOpen ? (
              <ChevronUp className="w-3 h-3 text-muted-foreground" />
            ) : (
              <ChevronDown className="w-3 h-3 text-muted-foreground" />
            )}
          </button>
        </div>
      </div>

      {/* Main Board Layout: Canvas with Post-its Layer and Optional Side/Bottom Dock */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        {/* Canvas Area with Absolute Sticky Notes */}
        <div
          className={`${
            isDataStructuresOpen ? "lg:col-span-8 xl:col-span-8" : "lg:col-span-12"
          } relative h-[640px] rounded-2xl overflow-hidden border border-border shadow-lg transition-all duration-200`}
        >
          <FreehandCanvas
            tool={tool}
            color={color}
            lineWidth={lineWidth}
            nodeLabel={nodeLabel}
            shapes={shapes}
            onShapesChange={handleShapesChange}
            canvasRef={canvasRef}
          />

          {/* Draggable Post-its Layer on Top of Canvas */}
          <StickyNotesLayer
            notes={notes}
            onUpdateNote={handleUpdateNote}
            onDeleteNote={handleDeleteNote}
          />

          {/* Mode Pill at Bottom Left */}
          <div className="absolute bottom-3 left-3 z-30 bg-card/85 backdrop-blur-md px-3 py-1.5 rounded-xl border border-border text-[11px] text-muted-foreground shadow-xs pointer-events-none">
            Modo: <strong className="text-foreground capitalize">{tool}</strong> • {shapes.length} formas • {notes.length} post-its
          </div>
        </div>

        {/* Live Interactive Data Structures Panel */}
        {isDataStructuresOpen && (
          <div className="lg:col-span-4 xl:col-span-4 flex flex-col gap-4">
            <DataStructuresPanel />
          </div>
        )}
      </div>
    </div>
  );
}
