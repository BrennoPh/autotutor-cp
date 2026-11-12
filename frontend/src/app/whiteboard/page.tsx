"use client";

import React, { useState, useEffect, Suspense } from "react";
import dynamic from "next/dynamic";
import { useSearchParams } from "next/navigation";
import { Breadcrumbs } from "@/components/navigation/Breadcrumbs";
import { Network, CheckCircle2, Table2, Cpu, PenTool, Layers } from "lucide-react";
import { GraphNode, GraphEdge } from "@/types/graphLab";

const RealWhiteboardWorkspace = dynamic(
  () =>
    import("@/components/whiteboard/RealWhiteboardWorkspace").then(
      (m) => m.RealWhiteboardWorkspace
    ),
  {
    ssr: false,
    loading: () => (
      <div className="h-[600px] bg-card/60 rounded-2xl border border-border animate-pulse flex items-center justify-center text-muted-foreground text-xs">
        Carregando lousa interativa e ferramentas de desenho...
      </div>
    ),
  }
);

const GraphLabWorkspace = dynamic(
  () =>
    import("@/components/whiteboard/GraphLabWorkspace").then(
      (m) => m.GraphLabWorkspace
    ),
  {
    ssr: false,
    loading: () => (
      <div className="h-[600px] bg-card/60 rounded-2xl border border-border animate-pulse flex items-center justify-center text-muted-foreground text-xs">
        Carregando estúdio de grafos...
      </div>
    ),
  }
);

const DpStudioWorkspace = dynamic(
  () =>
    import("@/components/whiteboard/DpStudioWorkspace").then(
      (m) => m.DpStudioWorkspace
    ),
  {
    ssr: false,
    loading: () => (
      <div className="h-[600px] bg-card/60 rounded-2xl border border-border animate-pulse flex items-center justify-center text-muted-foreground text-xs">
        Carregando estúdio de DP...
      </div>
    ),
  }
);

function WhiteboardLabInner() {
  const searchParams = useSearchParams();
  const source = searchParams.get("source");
  const modeParam = searchParams.get("mode");

  const [whiteboardMode, setWhiteboardMode] = useState<"board" | "graph" | "dp">(
    modeParam === "dp" ? "dp" : modeParam === "graph" ? "graph" : "board"
  );
  const [initialNodes, setInitialNodes] = useState<GraphNode[] | undefined>();
  const [initialEdges, setInitialEdges] = useState<GraphEdge[] | undefined>();
  const [fromStudyNotice, setFromStudyNotice] = useState<string | null>(null);

  useEffect(() => {
    try {
      const savedGraph = sessionStorage.getItem("autotutor_active_graph");
      if (savedGraph) {
        const parsed = JSON.parse(savedGraph);
        if (
          parsed.topic?.toLowerCase().includes("dinâmica") ||
          parsed.topic?.toLowerCase().includes("mochila") ||
          parsed.algorithm === "dp"
        ) {
          setWhiteboardMode("dp");
          setFromStudyNotice("Estudo de Programação Dinâmica carregado no DP Studio!");
        } else if (parsed.nodes && parsed.nodes.length > 0) {
          setInitialNodes(parsed.nodes);
          setInitialEdges(parsed.edges || []);
          setWhiteboardMode("graph");
          setFromStudyNotice("Topologia e código C++ importados do estudo com sucesso!");
        }
        sessionStorage.removeItem("autotutor_active_graph");
      }
    } catch (e) {
      console.warn("Erro ao ler grafo do estudo no sessionStorage:", e);
    }
  }, [source]);

  const breadcrumbs = [
    { label: "Dashboard", href: "/" },
    { label: "Quadro Branco & Estúdio de Simulação Algorítmica" },
  ];

  return (
    <main className="flex-1 flex flex-col min-w-0 pb-20 lg:pb-8">
      <header className="px-6 py-4 border-b border-border bg-card/40 backdrop-blur-sm sticky top-0 z-30">
        <Breadcrumbs items={breadcrumbs} />
      </header>

      <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              {whiteboardMode === "board" ? (
                <PenTool className="w-6 h-6 text-primary" />
              ) : whiteboardMode === "graph" ? (
                <Network className="w-6 h-6 text-primary" />
              ) : (
                <Table2 className="w-6 h-6 text-primary" />
              )}
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
                {whiteboardMode === "board"
                  ? "Quadro Branco & Estruturas de Dados"
                  : whiteboardMode === "graph"
                  ? "Simulador de Grafos & Árvores"
                  : "Estúdio de Programação Dinâmica (DP)"}
              </h1>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              {whiteboardMode === "board"
                ? "Lousa interativa livre para anotações com Post-its, desenho vetorial, nós e simulação de Pilha (LIFO) e Fila (FIFO)."
                : whiteboardMode === "graph"
                ? "Construa e simule algoritmos em grafos (DFS, BFS, Dijkstra) com Call Stack viva e prompts de IA."
                : "Visualize o preenchimento de matrizes DP, transições de estado de Bellman e memoization em tempo real."}
            </p>
          </div>

          {/* Studio Switcher Buttons: Board | Graph | DP */}
          <div className="flex items-center gap-1.5 bg-secondary/80 p-1 rounded-xl border border-border">
            <button
              type="button"
              onClick={() => setWhiteboardMode("board")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                whiteboardMode === "board"
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <PenTool className="w-3.5 h-3.5" />
              <span>Quadro Branco</span>
            </button>
            <button
              type="button"
              onClick={() => setWhiteboardMode("graph")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                whiteboardMode === "graph"
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Network className="w-3.5 h-3.5" />
              <span>Grafos & Árvores</span>
            </button>
            <button
              type="button"
              onClick={() => setWhiteboardMode("dp")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                whiteboardMode === "dp"
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Table2 className="w-3.5 h-3.5" />
              <span>Prog. Dinâmica (DP)</span>
            </button>
          </div>

          <button
            type="button"
            onClick={() => window.dispatchEvent(new CustomEvent("open-ai-config"))}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-colors border border-slate-700/60 bg-slate-900/60 ml-auto cursor-pointer"
            title="Configurações de Provedores de IA"
          >
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            <span className="hidden sm:inline">Configurações de API</span>
          </button>
        </div>

        {fromStudyNotice && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-slate-800 border border-slate-700/60 text-xs font-medium text-slate-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>{fromStudyNotice}</span>
          </div>
        )}

        {/* Mode Renders */}
        {whiteboardMode === "board" ? (
          <RealWhiteboardWorkspace />
        ) : whiteboardMode === "graph" ? (
          <GraphLabWorkspace
            initialNodes={initialNodes}
            initialEdges={initialEdges}
          />
        ) : (
          <DpStudioWorkspace />
        )}
      </div>
    </main>
  );
}

export default function WhiteboardLabPage() {
  return (
    <Suspense
      fallback={
        <main className="flex-1 p-6 space-y-6 max-w-7xl mx-auto w-full">
          <div className="h-8 w-64 bg-secondary/60 rounded-xl animate-pulse" />
          <div className="h-[600px] bg-card/60 rounded-2xl border border-border animate-pulse" />
        </main>
      }
    >
      <WhiteboardLabInner />
    </Suspense>
  );
}
