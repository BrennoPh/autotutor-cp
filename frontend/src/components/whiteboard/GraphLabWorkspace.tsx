"use client";

import React, { useState, useEffect, useRef } from "react";
import { GraphNode, GraphEdge, ExecutionStep, PlaybackStatus } from "@/types/graphLab";
import {
  generateDfsExecutionTape,
  generateBfsExecutionTape,
  generateBstExecutionTape,
  DFS_CODE_SNIPPET,
  BFS_CODE_SNIPPET,
  BST_CODE_SNIPPET,
} from "@/core/graphExecutionEngine";
import { whiteboardService, WhiteboardPromptResult } from "@/services/whiteboardService";
import { WhiteboardPromptBar } from "./WhiteboardPromptBar";
import { GraphCanvas } from "./GraphCanvas";
import { CodeTracerPanel } from "./CodeTracerPanel";
import { MemoryPanel } from "./MemoryPanel";
import { AutopsyTimelineBar } from "./AutopsyTimelineBar";
import { AutopsyResult } from "@/types/autopsy";
import {
  Play,
  Pause,
  SkipForward,
  SkipBack,
  RotateCcw,
  MousePointer,
  Link2,
  PlusCircle,
  FileCode,
  Code2,
  Terminal,
  Layers,
  Stethoscope,
} from "lucide-react";

const INITIAL_NODES: GraphNode[] = [
  { id: "1", x: 140, y: 160, label: "1", state: "unvisited" },
  { id: "2", x: 280, y: 80, label: "2", state: "unvisited" },
  { id: "3", x: 280, y: 240, label: "3", state: "unvisited" },
  { id: "4", x: 420, y: 160, label: "4", state: "unvisited" },
];

const INITIAL_EDGES: GraphEdge[] = [
  { id: "e1-2", from: "1", to: "2", directed: true, state: "normal" },
  { id: "e1-3", from: "1", to: "3", directed: true, state: "normal" },
  { id: "e2-4", from: "2", to: "4", directed: true, state: "normal" },
  { id: "e3-4", from: "3", to: "4", directed: true, state: "normal" },
];

const DEFAULT_USER_CODE_CPP = `#include <iostream>
#include <vector>
using namespace std;

// AutoTutor C++ Engine - Simulação Interativa
void dfs(int u, const vector<vector<int>>& adj, vector<bool>& vis) {
    vis[u] = true;
    for (int v : adj[u]) {
        if (!vis[v]) {
            dfs(v, adj, vis);
        }
    }
}`;

export interface GraphLabWorkspaceProps {
  initialNodes?: GraphNode[];
  initialEdges?: GraphEdge[];
  initialAlgorithm?: "dfs" | "bfs" | "dijkstra" | "bst";
  initialCode?: string;
  compact?: boolean;
}

export function GraphLabWorkspace({
  initialNodes,
  initialEdges,
  initialAlgorithm,
  initialCode,
  compact = false,
}: GraphLabWorkspaceProps = {}) {
  const [nodes, setNodes] = useState<GraphNode[]>(initialNodes || INITIAL_NODES);
  const [edges, setEdges] = useState<GraphEdge[]>(initialEdges || INITIAL_EDGES);
  const [canvasMode, setCanvasMode] = useState<"select" | "connect" | "add_node">("select");
  const [algorithm, setAlgorithm] = useState<"dfs" | "bfs" | "dijkstra" | "bst">(initialAlgorithm || "dfs");
  const [startNodeId, setStartNodeId] = useState<string>(initialNodes?.[0]?.id || "1");

  // Sync external presets when passed
  useEffect(() => {
    if (initialNodes && initialNodes.length > 0) {
      setNodes(initialNodes);
      setStartNodeId(initialNodes[0].id);
    }
  }, [initialNodes]);

  useEffect(() => {
    if (initialEdges && initialEdges.length > 0) {
      setEdges(initialEdges);
    }
  }, [initialEdges]);

  useEffect(() => {
    if (initialAlgorithm) {
      setAlgorithm(initialAlgorithm);
    }
  }, [initialAlgorithm]);

  useEffect(() => {
    if (initialCode) {
      setUserCode(initialCode);
    }
  }, [initialCode]);

  // Load active study graph from sessionStorage if redirected from Workspace/Arena
  useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const stored = sessionStorage.getItem("autotutor_active_graph");
        if (stored) {
          const parsed = JSON.parse(stored);
          if (parsed.nodes && parsed.nodes.length > 0) {
            setNodes(parsed.nodes);
            setStartNodeId(parsed.nodes[0].id);
          }
          if (parsed.edges && parsed.edges.length > 0) {
            setEdges(parsed.edges);
          }
          if (parsed.algorithm) {
            setAlgorithm(parsed.algorithm);
          }
          if (parsed.cpp_code) {
            setUserCode(parsed.cpp_code);
          }
          // Clear after loading so it doesn't overwrite future manual edits
          sessionStorage.removeItem("autotutor_active_graph");
        }
      } catch (err) {
        console.error("Erro ao carregar grafo do sessionStorage:", err);
      }
    }
  }, []);

  // Custom User Code Editor State
  const [userCode, setUserCode] = useState<string>(initialCode || DEFAULT_USER_CODE_CPP);
  const [rightPanelTab, setRightPanelTab] = useState<"editor" | "tracer">("editor");
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  // Custom Edge Modal State
  const [showEdgeModal, setShowEdgeModal] = useState(false);
  const [edgeInputText, setEdgeInputText] = useState("1 2\n1 3\n2 4\n3 4");

  // Playback state
  const [playbackStatus, setPlaybackStatus] = useState<PlaybackStatus>("idle");
  const [speedMs, setSpeedMs] = useState<number>(600);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [tape, setTape] = useState<ExecutionStep[]>([]);
  const [autopsyData, setAutopsyData] = useState<AutopsyResult | null>(null);
  const [isAutopsyRunning, setIsAutopsyRunning] = useState<boolean>(false);

  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Generate initial local tape whenever graph or algorithm configuration changes
  useEffect(() => {
    let newTape: ExecutionStep[] = [];
    if (algorithm === "dfs") {
      newTape = generateDfsExecutionTape(nodes, edges, startNodeId);
    } else if (algorithm === "bst") {
      newTape = generateBstExecutionTape(nodes, edges, 25);
    } else {
      newTape = generateBfsExecutionTape(nodes, edges, startNodeId);
    }
    setTape(newTape);
    setCurrentStepIndex(0);
    setPlaybackStatus("idle");
    if (timerRef.current) clearInterval(timerRef.current);
  }, [nodes, edges, algorithm, startNodeId]);

  // Playback loop
  useEffect(() => {
    if (playbackStatus === "playing") {
      timerRef.current = setInterval(() => {
        setCurrentStepIndex((prev) => {
          if (prev >= tape.length - 1) {
            setPlaybackStatus("completed");
            if (timerRef.current) clearInterval(timerRef.current);
            return prev;
          }
          return prev + 1;
        });
      }, speedMs);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [playbackStatus, tape.length, speedMs]);

  const currentStep = tape[currentStepIndex];

  // Execution Tracer via Backend / Custom Algorithm Runner
  const handleExecuteCustomCode = async () => {
    setIsSimulating(true);
    setPlaybackStatus("paused");

    try {
      const res = await whiteboardService.simulateAlgorithm({
        codeText: userCode,
        nodes: nodes,
        edges: edges,
        startNode: startNodeId,
        maxSteps: 500,
      });

      if (res.tape && res.tape.length > 0) {
        const mappedSteps: ExecutionStep[] = res.tape.map((s: any, idx: number) => ({
          stepIndex: idx,
          lineHighlighted: s.line || 1,
          memoryState: {
            visited: s.visited || {},
            stack: (s.call_stack || []).map((frameStr: string, fIdx: number) => ({
              functionName: frameStr,
              args: {},
              callDepth: fIdx,
              localVars: {},
            })),
            queue: s.queue || [],
            localVars: { u: s.active_node, edge: s.active_edge },
          },
          activeNodeId: s.active_node,
          activeEdgeId: s.active_edge,
          nodeStates: s.node_states || {},
          edgeStates: s.edge_states || {},
          logMessage: s.log || "",
        }));

        setTape(mappedSteps);
        setCurrentStepIndex(0);
        setRightPanelTab("tracer");
        setPlaybackStatus("playing");
      }
    } catch (e) {
      console.error("Falha na simulação personalizada:", e);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleRunAutopsy = async () => {
    setIsAutopsyRunning(true);
    setPlaybackStatus("paused");

    try {
      const res = await whiteboardService.runAutopsy({
        codeText: userCode,
        nodes,
        edges,
        algorithm,
        startNode: startNodeId,
        maxSteps: 200,
      });

      setAutopsyData(res);

      if (res.timeline && res.timeline.length > 0) {
        const mappedSteps: ExecutionStep[] = res.timeline.map((stepItem, idx) => {
          const visitedMap: Record<string, boolean> = {};
          stepItem.visited.forEach((v) => {
            visitedMap[v] = true;
          });

          const nodeStates: Record<string, any> = {};
          nodes.forEach((n) => {
            if (stepItem.active_node === n.id) {
              nodeStates[n.id] = "visiting";
            } else if (visitedMap[n.id]) {
              nodeStates[n.id] = "visited";
            } else {
              nodeStates[n.id] = "unvisited";
            }
          });

          const activeEdgeId = stepItem.active_edge
            ? `e${stepItem.active_edge.from}-${stepItem.active_edge.to}`
            : null;

          const edgeStates: Record<string, any> = {};
          edges.forEach((e) => {
            if (
              stepItem.active_edge &&
              ((e.from === stepItem.active_edge.from && e.to === stepItem.active_edge.to) ||
                (!e.directed && e.from === stepItem.active_edge.to && e.to === stepItem.active_edge.from))
            ) {
              edgeStates[e.id] = stepItem.event === "back_edge_cycle" ? "back_edge" : "traversed";
            } else {
              edgeStates[e.id] = "normal";
            }
          });

          return {
            stepIndex: idx,
            lineHighlighted: idx + 1,
            memoryState: {
              visited: visitedMap,
              stack: [],
              queue: Object.keys(visitedMap),
              localVars: stepItem.variables,
            },
            activeNodeId: stepItem.active_node,
            activeEdgeId,
            nodeStates,
            edgeStates,
            logMessage: `[${stepItem.event}] ${stepItem.explanation}`,
          };
        });

        setTape(mappedSteps);
        setCurrentStepIndex(0);
        setPlaybackStatus("idle");
      }
    } catch (err) {
      console.error("Falha ao executar autópsia algorítmica:", err);
    } finally {
      setIsAutopsyRunning(false);
    }
  };

  // Playback Handlers
  const handlePlayPause = () => {
    if (playbackStatus === "playing") {
      setPlaybackStatus("paused");
    } else {
      if (currentStepIndex >= tape.length - 1) {
        setCurrentStepIndex(0);
      }
      setPlaybackStatus("playing");
    }
  };

  const handleStepForward = () => {
    setPlaybackStatus("paused");
    setCurrentStepIndex((prev) => Math.min(tape.length - 1, prev + 1));
  };

  const handleStepBackward = () => {
    setPlaybackStatus("paused");
    setCurrentStepIndex((prev) => Math.max(0, prev - 1));
  };

  const handleReset = () => {
    setPlaybackStatus("idle");
    setCurrentStepIndex(0);
  };

  // Preset Loaders
  const loadPreset = (preset: "dag" | "cycle" | "disconnected" | "bst") => {
    if (preset === "bst") {
      setNodes([
        { id: "20", x: 260, y: 70, label: "20", state: "unvisited" },
        { id: "10", x: 160, y: 160, label: "10", state: "unvisited" },
        { id: "30", x: 360, y: 160, label: "30", state: "unvisited" },
        { id: "5", x: 110, y: 260, label: "5", state: "unvisited" },
        { id: "15", x: 210, y: 260, label: "15", state: "unvisited" },
        { id: "25", x: 310, y: 260, label: "25 (Alvo)", state: "unvisited" },
        { id: "35", x: 410, y: 260, label: "35", state: "unvisited" },
      ]);
      setEdges([
        { id: "e20-10", from: "20", to: "10", directed: true, state: "normal" },
        { id: "e20-30", from: "20", to: "30", directed: true, state: "normal" },
        { id: "e10-5", from: "10", to: "5", directed: true, state: "normal" },
        { id: "e10-15", from: "10", to: "15", directed: true, state: "normal" },
        { id: "e30-25", from: "30", to: "25", directed: true, state: "normal" },
        { id: "e30-35", from: "30", to: "35", directed: true, state: "normal" },
      ]);
      setStartNodeId("20");
      setAlgorithm("bst");
      setUserCode(BST_CODE_SNIPPET.join("\n"));
      return;
    }

    if (preset === "dag") {
      setNodes([
        { id: "1", x: 100, y: 160, label: "1", state: "unvisited" },
        { id: "2", x: 240, y: 90, label: "2", state: "unvisited" },
        { id: "3", x: 240, y: 230, label: "3", state: "unvisited" },
        { id: "4", x: 380, y: 160, label: "4", state: "unvisited" },
        { id: "5", x: 500, y: 160, label: "5", state: "unvisited" },
      ]);
      setEdges([
        { id: "e1-2", from: "1", to: "2", directed: true, state: "normal" },
        { id: "e1-3", from: "1", to: "3", directed: true, state: "normal" },
        { id: "e2-4", from: "2", to: "4", directed: true, state: "normal" },
        { id: "e3-4", from: "3", to: "4", directed: true, state: "normal" },
        { id: "e4-5", from: "4", to: "5", directed: true, state: "normal" },
      ]);
      setStartNodeId("1");
    } else if (preset === "cycle") {
      setNodes([
        { id: "1", x: 180, y: 90, label: "1", state: "unvisited" },
        { id: "2", x: 360, y: 90, label: "2", state: "unvisited" },
        { id: "3", x: 360, y: 240, label: "3", state: "unvisited" },
        { id: "4", x: 180, y: 240, label: "4", state: "unvisited" },
      ]);
      setEdges([
        { id: "e1-2", from: "1", to: "2", directed: true, state: "normal" },
        { id: "e2-3", from: "2", to: "3", directed: true, state: "normal" },
        { id: "e3-4", from: "3", to: "4", directed: true, state: "normal" },
        { id: "e4-1", from: "4", to: "1", directed: true, state: "normal" }, // Back-edge
      ]);
      setStartNodeId("1");
    } else if (preset === "disconnected") {
      setNodes([
        { id: "1", x: 120, y: 120, label: "1", state: "unvisited" },
        { id: "2", x: 260, y: 120, label: "2", state: "unvisited" },
        { id: "3", x: 120, y: 260, label: "3", state: "unvisited" },
        { id: "4", x: 260, y: 260, label: "4", state: "unvisited" },
      ]);
      setEdges([
        { id: "e1-2", from: "1", to: "2", directed: true, state: "normal" },
        { id: "e3-4", from: "3", to: "4", directed: true, state: "normal" },
      ]);
      setStartNodeId("1");
    }
  };

  const handlePromptGenerated = (result: WhiteboardPromptResult) => {
    if (result.nodes && result.nodes.length > 0) {
      setNodes(result.nodes);
      setStartNodeId(result.nodes[0].id);
    }
    if (result.edges && result.edges.length > 0) {
      setEdges(result.edges);
    }
    if (
      result.algorithm === "bst" ||
      result.title?.toLowerCase().includes("bst") ||
      result.title?.toLowerCase().includes("busca")
    ) {
      setAlgorithm("bst");
    } else if (result.algorithm) {
      setAlgorithm(result.algorithm);
    }
    if (result.cpp_code) {
      setUserCode(result.cpp_code);
    }
  };

  const handleImportGraph = async () => {
    try {
      const res = await whiteboardService.parseGraph(edgeInputText);
      if (res.nodes && res.nodes.length > 0) {
        setNodes(res.nodes);
        setEdges(res.edges);
        setStartNodeId(res.nodes[0].id);
        setShowEdgeModal(false);
      }
    } catch (e) {
      console.error("Falha ao processar grafo:", e);
    }
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* AI Whiteboard Prompt Bar */}
      <WhiteboardPromptBar onGenerated={handlePromptGenerated} />

      {/* Top Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-card border border-border rounded-2xl shadow-sm">
        {/* Canvas Tools */}
        <div className="flex items-center gap-1.5 bg-secondary/80 p-1 rounded-xl border border-border">
          <button
            onClick={() => setCanvasMode("select")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              canvasMode === "select"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
            title="Arrastar e mover nós"
          >
            <MousePointer className="w-3.5 h-3.5" />
            <span>Mover</span>
          </button>
          <button
            onClick={() => setCanvasMode("connect")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              canvasMode === "connect"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
            title="Arrastar de um nó até outro para criar aresta"
          >
            <Link2 className="w-3.5 h-3.5" />
            <span>Conectar</span>
          </button>
          <button
            onClick={() => setCanvasMode("add_node")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              canvasMode === "add_node"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
            title="Clicar na tela para adicionar novo nó"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>Adicionar Nó</span>
          </button>
        </div>

        {/* Algorithm, Start Node & Presets */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Start Node Selector */}
          <div className="flex items-center gap-1 text-xs text-muted-foreground bg-secondary/60 px-2.5 py-1.5 rounded-xl border border-border">
            <span>Raiz:</span>
            <select
              value={startNodeId}
              onChange={(e) => setStartNodeId(e.target.value)}
              className="bg-transparent text-foreground text-xs font-bold focus:outline-none"
            >
              {nodes.map((n) => (
                <option key={n.id} value={n.id} className="bg-card text-foreground">
                  Nó {n.label || n.id}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-1 text-xs">
            <span className="text-muted-foreground">Presets:</span>
            <button
              onClick={() => loadPreset("bst")}
              className="px-2 py-1 bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 rounded-lg text-xs font-semibold transition-colors"
              title="Árvore Binária de Busca com Busca Binária do valor 25"
            >
              BST (Busca)
            </button>
            <button
              onClick={() => loadPreset("dag")}
              className="px-2 py-1 bg-secondary hover:bg-accent rounded-lg text-xs text-foreground transition-colors"
            >
              DAG
            </button>
            <button
              onClick={() => loadPreset("cycle")}
              className="px-2 py-1 bg-secondary hover:bg-accent rounded-lg text-xs text-foreground transition-colors"
            >
              Ciclo
            </button>
            <button
              onClick={() => loadPreset("disconnected")}
              className="px-2 py-1 bg-secondary hover:bg-accent rounded-lg text-xs text-foreground transition-colors"
              title="Dois componentes desconexos"
            >
              Desconexo
            </button>
            <button
              onClick={() => setShowEdgeModal(true)}
              className="flex items-center gap-1 px-2 py-1 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 rounded-lg text-xs font-semibold transition-colors"
              title="Inserir lista de arestas personalizada"
            >
              <FileCode className="w-3 h-3" />
              <span>Arestas</span>
            </button>
            <button
              type="button"
              onClick={handleRunAutopsy}
              disabled={isAutopsyRunning}
              className="flex items-center gap-1.5 px-2.5 py-1 bg-rose-600/15 hover:bg-rose-600/25 text-rose-300 border border-rose-500/30 rounded-lg text-xs font-semibold transition-all disabled:opacity-50"
              title="Disparar motor de autópsia algorítmica e análise temporal"
            >
              <Stethoscope className={`w-3.5 h-3.5 text-rose-400 ${isAutopsyRunning ? "animate-spin" : ""}`} />
              <span>{isAutopsyRunning ? "Analisando..." : "Autópsia C++"}</span>
            </button>
          </div>
        </div>

        {/* Playback Controls Bar */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            className="p-2 rounded-xl border border-border hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
            title="Reiniciar Simulação"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={handleStepBackward}
            disabled={currentStepIndex === 0}
            className="p-2 rounded-xl border border-border hover:bg-secondary disabled:opacity-40 transition-colors"
            title="Passo Anterior"
          >
            <SkipBack className="w-4 h-4" />
          </button>
          <button
            onClick={handlePlayPause}
            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-primary-foreground rounded-xl text-xs font-bold hover:bg-primary-hover shadow-sm transition-all"
          >
            {playbackStatus === "playing" ? (
              <>
                <Pause className="w-4 h-4" />
                <span>Pausar</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Reproduzir</span>
              </>
            )}
          </button>
          <button
            onClick={handleStepForward}
            disabled={currentStepIndex >= tape.length - 1}
            className="p-2 rounded-xl border border-border hover:bg-secondary disabled:opacity-40 transition-colors"
            title="Próximo Passo"
          >
            <SkipForward className="w-4 h-4" />
          </button>

          {/* Speed Slider */}
          <div className="hidden sm:flex items-center gap-2 pl-2 border-l border-border text-xs text-muted-foreground">
            <span>Velocidade:</span>
            <input
              type="range"
              min="150"
              max="1500"
              step="50"
              value={speedMs}
              onChange={(e) => setSpeedMs(Number(e.target.value))}
              className="w-20 accent-primary cursor-pointer"
            />
            <span className="font-mono text-[11px]">{speedMs}ms</span>
          </div>
        </div>
      </div>

      {/* Main Split-View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1 min-h-[600px]">
        {/* Left Canvas (7 cols) */}
        <div className="lg:col-span-7 flex flex-col h-full space-y-2">
          <div className="flex-1 h-full min-h-[480px]">
            <GraphCanvas
              nodes={nodes}
              edges={edges}
              nodeStates={currentStep?.nodeStates}
              edgeStates={currentStep?.edgeStates}
              activeNodeId={currentStep?.activeNodeId}
              activeEdgeId={currentStep?.activeEdgeId}
              mode={canvasMode}
              onNodesChange={setNodes}
              onEdgesChange={setEdges}
            />
          </div>
          {/* Time Machine Autopsy Timeline Bar */}
          <AutopsyTimelineBar
            currentStepIndex={currentStepIndex}
            totalSteps={tape.length}
            playbackStatus={playbackStatus}
            failureStep={autopsyData?.failure_step}
            failureReason={autopsyData?.failure_reason}
            currentExplanation={
              autopsyData?.timeline?.[currentStepIndex]?.explanation || currentStep?.logMessage
            }
            currentEvent={autopsyData?.timeline?.[currentStepIndex]?.event}
            speedMs={speedMs}
            onStepChange={(newIdx) => {
              setPlaybackStatus("paused");
              setCurrentStepIndex(newIdx);
            }}
            onPlayPause={handlePlayPause}
            onReset={handleReset}
            onSpeedChange={setSpeedMs}
            className="mt-1"
          />
        </div>

        {/* Right Split: Code & Memory Panels (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-4 h-full min-h-[600px]">
          {/* Top Panel: Toggle between Custom Editor & Visual Line Tracer */}
          <div className="bg-card border border-border rounded-2xl overflow-hidden flex flex-col shadow-sm">
            <div className="p-2 border-b border-border bg-secondary/40 flex items-center justify-between">
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => setRightPanelTab("editor")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    rightPanelTab === "editor"
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Code2 className="w-3.5 h-3.5" />
                  <span>Editor de Código</span>
                </button>
                <button
                  type="button"
                  onClick={() => setRightPanelTab("tracer")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    rightPanelTab === "tracer"
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Terminal className="w-3.5 h-3.5" />
                  <span>Rastreador de Linhas</span>
                </button>
              </div>

              {rightPanelTab === "editor" && (
                <button
                  type="button"
                  onClick={handleExecuteCustomCode}
                  disabled={isSimulating}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 text-white rounded-xl text-xs font-bold hover:bg-emerald-500 shadow-sm transition-all disabled:opacity-50"
                >
                  <Play className={`w-3.5 h-3.5 ${isSimulating ? "animate-spin" : ""}`} />
                  <span>{isSimulating ? "Rastreando..." : "Executar no Grafo"}</span>
                </button>
              )}
            </div>

            {rightPanelTab === "editor" ? (
              <div className="p-3 space-y-2">
                <textarea
                  value={userCode}
                  onChange={(e) => setUserCode(e.target.value)}
                  rows={8}
                  spellCheck={false}
                  className="w-full p-3 rounded-xl bg-background text-foreground font-mono text-xs focus:outline-none border border-border resize-none leading-relaxed"
                  placeholder="Escreva seu algoritmo em C++17..."
                />
                <div className="flex items-center justify-between text-[11px] text-muted-foreground px-1">
                  <span>Suporta DFS / BFS / Dijkstra em C++ com <code className="text-primary font-mono">adj[u]</code></span>
                  <span>Limite: máx 500 passos</span>
                </div>
              </div>
            ) : (
              <div className="h-56 overflow-hidden">
                <CodeTracerPanel
                  codeLines={userCode.split("\n")}
                  activeLineIndex={currentStep?.lineHighlighted || 1}
                  title="Execução do Código do Aluno"
                />
              </div>
            )}
          </div>

          {/* Live Memory & State Panel */}
          <div className="flex-1 min-h-[300px]">
            <MemoryPanel
              memoryState={currentStep?.memoryState}
              logMessage={currentStep?.logMessage}
            />
          </div>
        </div>
      </div>

      {/* Custom Edges Input Modal */}
      {showEdgeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-card border border-border rounded-2xl p-5 shadow-2xl space-y-4">
            <div>
              <h3 className="text-sm font-bold text-foreground">Importar Grafo Personalizado</h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                Digite um par de nós por linha (ex: &quot;1 2&quot; ou &quot;A B&quot;) para construir o grafo dinamicamente.
              </p>
            </div>

            <textarea
              value={edgeInputText}
              onChange={(e) => setEdgeInputText(e.target.value)}
              rows={6}
              className="w-full p-3 rounded-xl bg-secondary/50 border border-border font-mono text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="1 2&#10;1 3&#10;2 4&#10;3 4"
            />

            <div className="flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowEdgeModal(false)}
                className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-secondary text-foreground hover:bg-accent"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleImportGraph}
                className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:opacity-90"
              >
                Gerar Grafo
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
